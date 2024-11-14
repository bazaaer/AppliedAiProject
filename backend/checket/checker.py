import torch
from sentence_transformers import SentenceTransformer

class SimilarityEvaluator:
    def __init__(self, training_embeddings_path, device=None):
        self.device = (
            device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model = SentenceTransformer(
            "ODeNy/Checket_Antwerpen_Huisstijl_MiniLM", device=device
        )
        self.training_embeddings = torch.load(
            training_embeddings_path, weights_only=True
        ).to(self.device)

    def topk_mean_similarity_score(self, new_sentence, k=5):
        new_embedding = self.model.encode(
            new_sentence, convert_to_tensor=True, device=self.device
        )

        similarities = self.model.similarity(
            new_embedding.unsqueeze(0), self.training_embeddings
        )

        mean_topk_score = torch.topk(similarities, k).values.mean().item()

        return new_sentence, mean_topk_score


# Usage
if __name__ == "__main__":
    training_embeddings_path = "embeddings.pt"

    similarity_evaluator = SimilarityEvaluator(training_embeddings_path)

    sentence, score = similarity_evaluator.topk_mean_similarity_score(
        """De Britse realityster en presentatrice <strong>Narinder Kaur</strong> (51) ligt zwaar onder vuur na haar uithaal naar prinses Kate op "X"."""
    )

    print(f"Sentence: {sentence}\nTop-K Mean Similarity Score: {score:.8f}")
