import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer

# Load the model
model_path = "output/paraphrase-multilingual-MiniLM-L12-v2/final"
model = SentenceTransformer(model_path)

# Load training data
training_data_path = "cleaned_training.csv"
training_data = pd.read_csv(training_data_path)

# Sample 10% of the data (adjust the fraction as needed)
sampled_training_data = training_data.sample(frac=0.1, random_state=42)
training_sentences = sampled_training_data['sentence1'].tolist()  # Replace 'sentence1' with the actual column name

# Encode and save the training data embeddings (only needs to be run once)
training_embeddings = model.encode(training_sentences, convert_to_tensor=True)

# Save embeddings and sentences to a file (only needs to be run once)
with open("training_embeddings.pkl", "wb") as f:
    pickle.dump(training_embeddings, f)