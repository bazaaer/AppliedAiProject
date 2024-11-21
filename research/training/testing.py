import time

import torch
from sentence_transformers import SentenceTransformer

model_path = "output/finetuned_paraphrase-multilingual-mpnet-base-v2/final"
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(model_path, device=device)

def topk_mean_similarity_score(new_sentence, k=5):
    new_embedding = model.encode(new_sentence, convert_to_tensor=True, device=device)

    training_embeddings = torch.load("training_embeddings.pt", weights_only=True)
    training_embeddings = training_embeddings.to(device)

    similarities = model.similarity(new_embedding, training_embeddings)

    mean_topk_score = torch.topk(similarities, k).values.mean().item()

    print(f"Top-{k} mean similarity score for '{new_sentence[:50]}': {mean_topk_score:.3f}")

bad_sentence = "Waarschijnlijk was methanol de oorzaak van de drank, wat leidde tot een reeks ziekenhuisbezoeken, waaronder dat van een Nederlandse. Minstens tien anderen volgden, in een reeks van onvermijdelijke gebeurtenissen op 21/11/2024."
topk_mean_similarity_score(bad_sentence, k=150)

good_sentence = "Minstens 10 anderen zijn naar het ziekenhuis gebracht, waaronder 1 persoon uit Nederland, op 21 november 2024. Vermoedelijk zat er methanol in hun drankje."
topk_mean_similarity_score(good_sentence, k=150)

new_sentence = "De baggerwerken voor de toekomstige Scheldetunnel worden daarbij archeologisch begeleid omdat er in het Scheldeslib nog heel wat vondsten verscholen zitten."
topk_mean_similarity_score(new_sentence, k=150)