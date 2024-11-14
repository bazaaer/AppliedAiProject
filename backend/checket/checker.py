import torch
from sentence_transformers import SentenceTransformer

class SimilarityEvaluator:
    def __init__(self, base_embeddings_path, device=None):
        self.device = (
            device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        )

        self.model = SentenceTransformer(
            "ODeNy/Checket_Antwerpen_Huisstijl_MiniLM", device=device
        )

        self.base_embeddings = torch.load(
            base_embeddings_path, weights_only=True
        ).to(self.device)

    def topk_mean_similarity_score(self, sentence, k=5):
        embedding = self.model.encode(
            sentence, convert_to_tensor=True, device=self.device
        )

        similarities = self.model.similarity(
            embedding.unsqueeze(0), self.base_embeddings
        )

        mean_topk_score = torch.topk(similarities, k).values.mean().item()

        return mean_topk_score


# Usage
if __name__ == "__main__":
    training_embeddings_path = "embeddings.pt"

    similarity_evaluator = SimilarityEvaluator(training_embeddings_path)

    sentence = """Sinterklaas arriveert aan het stadhuis rond 14.45 uur en zal daar, vanop het balkon aan het Schoon Verdiep, de kinderen en hun mama’s en papa’s toespreken."""

    score = similarity_evaluator.topk_mean_similarity_score(sentence,k=8)

    print(f"Sentence: {sentence}\nTop-K Mean Similarity Score: {score:.3f}")
