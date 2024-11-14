import torch
from sentence_transformers import SentenceTransformer

class SimilarityEvaluator:
    def __init__(self, model_path, training_embeddings_path, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SentenceTransformer(model_path, device=self.device)
        self.training_embeddings = torch.load(training_embeddings_path,weights_only=True).to(self.device)

    def topk_mean_similarity_score(self, new_sentence, k=5):
        new_embedding = self.model.encode(new_sentence, convert_to_tensor=True, device=self.device)

        similarities = self.model.similarity(new_embedding.unsqueeze(0), self.training_embeddings)

        mean_topk_score = torch.topk(similarities, k).values.mean().item()

        return new_sentence, mean_topk_score

# Usage
if __name__ == "__main__":
    model_path = "finetuned_paraphrase-multilingual-MiniLM-L12-v2"
    training_embeddings_path = "embeddings.pt"

    similarity_evaluator = SimilarityEvaluator(model_path, training_embeddings_path)

    sentence, score = similarity_evaluator.topk_mean_similarity_score("De herfstkou verdrijf je deze week door te dansen of naar het museum te gaan. Leer swingen zoals in James Ensors tijd of ga clubben in het Centraal Station en andere speciale locaties.")
    print(f"Sentence: {sentence}\nTop-K Mean Similarity Score: {score:.8f}")
