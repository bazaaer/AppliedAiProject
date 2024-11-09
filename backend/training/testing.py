import pickle
import torch
from sentence_transformers import SentenceTransformer

# Load the model
model_path = "output/paraphrase-multilingual-MiniLM-L12-v2/final"
model = SentenceTransformer(model_path)

# Function to calculate the top-k mean similarity score between a new sentence and training data
def topk_mean_similarity_score(new_sentence, k=5):
    # Encode the new sentence
    new_embedding = model.encode(new_sentence, convert_to_tensor=True)

    # Load training embeddings
    with open("training_embeddings.pkl", "rb") as f:
        training_embeddings = pickle.load(f)

    # Calculate cosine similarity between the new embedding and each training embedding
    similarities = torch.nn.functional.cosine_similarity(new_embedding, training_embeddings)

    # Sort similarities to get the top-k highest values
    topk_similarities, _ = torch.topk(similarities, k)

    # Calculate the mean of the top-k similarity scores
    mean_topk_score = topk_similarities.mean().item()

    # Print the top-k mean similarity score
    print(f"Top-{k} mean similarity score for '{new_sentence[:50]}': {mean_topk_score:.3f}")

# Example of comparing a new sentence with top-k scoring
print("goede herschreven zinnen")
new_sentence1 = "Bij een noodsituatie zoals een grote brand, een overstroming of een stroomonderbreking stuurt BE-Alert automatisch berichten uit."
topk_mean_similarity_score(new_sentence1, k=25)

new_sentence2 = "In een noodgeval zoals een grote brand, een overstroming of een stroomuitval, waarschuwt BE-Alert ons direct via sms."
topk_mean_similarity_score(new_sentence2, k=25)

print("-" * 50)

print("slechte herschreven zinnen")
new_sentence3 = "Spoor borstkanker tijdig op Borstkanker is de meest voorkomende kanker bij vrouwen in Vlaanderen."
topk_mean_similarity_score(new_sentence3, k=25)

new_sentence4 = "Ontdek borstkanker snel - Borstkanker is de meest voorkomende kanker bij vrouwen in Vlaanderen."
topk_mean_similarity_score(new_sentence4, k=25)