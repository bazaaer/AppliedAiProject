from ray import serve
from starlette.requests import Request
from grouper import SentenceGrouper
from checker import SimilarityEvaluator
from ray.serve.handle import DeploymentHandle


@serve.deployment(ray_actor_options={"num_gpus": 0.2})
class SentenceGrouperDeployment:
    """
    A deployment wrapper for the SentenceGrouper class.
    """

    def __init__(self, model: str = "nl_core_news_md", similarity_threshold: float = 0.75):
        self.grouper = SentenceGrouper(model=model, similarity_threshold=similarity_threshold)

    async def process(self, text: str):
        return self.grouper.group_consecutive_similar_sentences(text)

    async def __call__(self, request: dict):
        request_data = request

        text = request_data.get("text", "")
        result = [sentence[0] for sentence in await self.process(text)]
        return {"sentences": result}


@serve.deployment(ray_actor_options={"num_gpus": 0.8})
class SimilarityEvaluatorDeployment:
    """
    A deployment wrapper for the SimilarityEvaluator class.
    """

    def __init__(self, training_embeddings_path: str, top_k: int = 8):
        self.evaluator = SimilarityEvaluator(training_embeddings_path)
        self.top_k = top_k

    async def process(self, sentences: list):
        return [
            {"sentence": sentence, "score": self.evaluator.topk_mean_similarity_score(sentence, k=self.top_k)}
            for sentence in sentences
        ]

    async def __call__(self, request: dict):
        request_data = request

        sentences = request_data.get("sentences", [])
        result = await self.process(sentences)
        return {"sentence_scores": result}


@serve.deployment
class Pipeline:
    """
    A pipeline that chains SentenceGrouperDeployment and SimilarityEvaluatorDeployment.
    """

    def __init__(self, grouper: DeploymentHandle, evaluator: DeploymentHandle):
        self.grouper = grouper
        self.evaluator = evaluator

    async def process(self, text: str):
        grouper_result = await self.grouper.remote({"text": text})

        evaluator_result = await self.evaluator.remote(grouper_result)

        return evaluator_result

    async def __call__(self, request: Request):
        request_data = await request.json()
        text = request_data.get("text", "")
        result = await self.process(text)
        return result


# Bind the deployments together
grouper_app = SentenceGrouperDeployment.bind(model="nl_core_news_md", similarity_threshold=0.80)
evaluator_app = SimilarityEvaluatorDeployment.bind(training_embeddings_path="embeddings.pt", top_k=8)
pipeline_app = Pipeline.bind(grouper_app, evaluator_app)
