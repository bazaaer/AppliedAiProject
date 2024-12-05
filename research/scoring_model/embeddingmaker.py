import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

model_path = "/output/finetuned_paraphrase-multilingual-mpnet-base-v2/final"
model = SentenceTransformer(model_path)

training_data_path = "cleaned_training.csv"
training_data = pd.read_csv(training_data_path)
df = training_data["sentence1"]
df.drop_duplicates(inplace=True)
sampled_training_data = df.sample(frac=0.15, random_state=42)
training_sentences = sampled_training_data.tolist()

training_embeddings = model.encode(training_sentences, convert_to_tensor=True)

torch.save(training_embeddings, "training_embeddings.pt")
