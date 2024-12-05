from ray import serve
from grouper import SentenceGrouper
from checker import SimilarityEvaluator
from starlette.requests import Request

@serve.deployment(ray_actor_options={"num_gpus": 0.1, "num_cpus": 1})
class CombinedPipeline:
    """
    Combines SentenceGrouper and SimilarityEvaluator into a single deployment.
    Supports batch processing and shared memory caching for intermediate data.
    """

    def __init__(self, model: str, similarity_threshold: float, training_embeddings_path: str, top_k: int = 8):
        # Initialize SentenceGrouper and SimilarityEvaluator
        self.grouper = SentenceGrouper(model=model, similarity_threshold=similarity_threshold)
        self.evaluator = SimilarityEvaluator(training_embeddings_path)
        self.top_k = top_k
        # Initialize Ray object store for caching
        self.cache = {}

    async def process_single_text(self, text: str):
        """
        Process a single text to group sentences and evaluate similarity scores.
        """
        # Check cache for precomputed embeddings
        if text in self.cache:
            grouped_sentences = self.cache[text]
        else:
            grouped_sentences = self.grouper.group_consecutive_similar_sentences(text)
            self.cache[text] = grouped_sentences  # Store in cache

        sentences = [sentence[0] for sentence in grouped_sentences]

        # Evaluate similarity for each grouped sentence
        sentence_scores = [
            {"sentence": sentence, "score": self.evaluator.topk_mean_similarity_score(sentence, k=self.top_k)}
            for sentence in sentences
        ]
        return sentence_scores

    async def process_batch(self, texts: list):
        """
        Process a batch of texts for sentence grouping and similarity evaluation.
        """
        results = []
        for text in texts:
            results.extend(await self.process_single_text(text))
        return results

    async def __call__(self, request: Request):
        """
        Handle incoming requests for batch or single-text processing.
        """
        request_data = await request.json()
        texts = request_data.get("text", [])
        print(texts)
        
        # Process batch or single text
        if isinstance(texts, list):
            result = await self.process_batch(texts)
        else:
            result = await self.process_single_text(texts)
        
        return {"sentence_scores": result}


# Create the deployment
pipeline_app = CombinedPipeline.bind(
    model="nl_core_news_md",
    similarity_threshold=0.80,
    training_embeddings_path="embeddings.pt",
    top_k=8,
)
