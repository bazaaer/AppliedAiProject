import torch
from sentence_transformers import SentenceTransformer
from typing import Optional


class SimilarityEvaluator:
    """
    A class to evaluate the similarity of a given sentence with a set of base embeddings.

    This class loads precomputed base embeddings and uses a pre-trained SentenceTransformer
    model to compute the similarity between an input sentence and the base embeddings.
    The `topk_mean_similarity_score` method returns the average similarity of the top-k
    most similar base embeddings to the input sentence.

    Attributes:
        device (str): The device to perform computation on, either 'cuda' or 'cpu'.
        model (SentenceTransformer): The sentence transformer model for encoding and similarity calculations.
        base_embeddings (torch.Tensor): The precomputed embeddings to compare against.

    Methods:
        topk_mean_similarity_score(sentence: str, k: int = 5) -> float:
            Calculates the mean similarity score of the top-k similar embeddings to the input sentence.
    """
    def __init__(self, base_embeddings_path: str, device: Optional[str] = None):
        """
        Initializes the SimilarityEvaluator with precomputed embeddings and a SentenceTransformer model.

        Args:
            base_embeddings_path (str): Path to the saved base embeddings.
            device (Optional[str], optional): Device to run the computations ('cuda' or 'cpu').
                                              If not provided, defaults to 'cuda' if available.
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = SentenceTransformer("ODeNy/Checket_Antwerpen_Huisstijl_MiniLM", device=device)

        self.base_embeddings = torch.load(base_embeddings_path, weights_only=True).to(self.device)

    def topk_mean_similarity_score(self, sentence: str, k: int = 5) -> float:
        """
        Calculates the mean similarity score for the top-k most similar embeddings to the input sentence.

        Args:
            sentence (str): The input sentence to evaluate.
            k (int, optional): The number of top similar embeddings to consider. Defaults to 5.

        Returns:
            float: The mean similarity score of the top-k similar embeddings.
        """
        embedding = self.model.encode(sentence, convert_to_tensor=True, device=self.device)

        similarities = self.model.similarity(embedding.unsqueeze(0), self.base_embeddings)

        mean_topk_score = torch.topk(similarities, k).values.mean().item()

        return mean_topk_score

# Usage
if __name__ == "__main__":
    training_embeddings_path = "embeddings.pt"

    similarity_evaluator = SimilarityEvaluator(training_embeddings_path)

    sentence = """Sinterklaas arriveert aan het stadhuis rond 14.45 uur en zal daar, vanop het balkon aan het Schoon Verdiep, de kinderen en hun mama’s en papa’s toespreken."""

    score = similarity_evaluator.topk_mean_similarity_score(sentence,k=8)

    print(f"Sentence: {sentence}\nTop-K Mean Similarity Score: {score:.3f}")
