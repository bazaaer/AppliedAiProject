import torch
from sentence_transformers import SentenceTransformer
import time

model_path = "output/paraphrase-multilingual-MiniLM-L12-v2/final"
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(model_path, device=device)

def topk_mean_similarity_score(new_sentence, k=5):
    total_start = time.time()

    new_embedding = model.encode(new_sentence, convert_to_tensor=True, device=device)

    training_embeddings = torch.load("training_embeddings.pt")
    training_embeddings = training_embeddings.to(device)

    similarities = model.similarity(new_embedding, training_embeddings)

    mean_topk_score = torch.topk(similarities, k).values.mean().item()

    print(f"Top-{k} mean similarity score for '{new_sentence[:50]}': {mean_topk_score:.3f}")

new_sentence = "In een noodgeval zoals een grote brand, een overstroming of een stroomuitval, waarschuwt BE-Alert ons direct via sms."
topk_mean_similarity_score(new_sentence, k=25)
