import pandas as pd
import torch
from datasets import Dataset
from sentence_transformers import (
    InputExample,
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
)
from sentence_transformers.evaluation import (
    EmbeddingSimilarityEvaluator,
    SimilarityFunction,
)
from sentence_transformers.losses import CoSENTLoss

# Ensure that CUDA is available and set the device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the pre-trained SentenceTransformer model
# NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name).to(device)  # Move model to GPU

# Load your dataset
df = pd.read_csv("../cleaned_training.csv")

# Prepare training examples
train_examples = [
    InputExample(texts=[row["sentence1"], row["sentence2"]], label=float(row["score"]))
    for _, row in df.iterrows()
]

# Split into train and eval datasets
train_size = int(0.8 * len(train_examples))
train_set = train_examples[:train_size]
eval_set = train_examples[train_size:]

train_data = {
    "sentence1": [ex.texts[0] for ex in train_set],
    "sentence2": [ex.texts[1] for ex in train_set],
    "score": [ex.label for ex in train_set],
}
eval_data = {
    "sentence1": [ex.texts[0] for ex in eval_set],
    "sentence2": [ex.texts[1] for ex in eval_set],
    "score": [ex.label for ex in eval_set],
}

train_df = pd.DataFrame(train_data)
eval_df = pd.DataFrame(eval_data)

train_dataset = Dataset.from_pandas(train_df)
eval_dataset = Dataset.from_pandas(eval_df)

loss = CoSENTLoss(model)

# Set training arguments
args = SentenceTransformerTrainingArguments(
    # Output configuration
    output_dir="../training/output/paraphrase-multilingual-MiniLM-L12-v2",
    # Training performance parameters
    warmup_steps=64,
    num_train_epochs=2,  # Total number of epochs to train
    learning_rate=2e-5,  # Learning rate for the optimizer
    lr_scheduler_type="linear",  # Scheduler type
    per_device_train_batch_size=32,  # Batch size for training
    per_device_eval_batch_size=32,  # Batch size for evaluation
    fp16=True,  # Enable 16-bit floating point precision for faster training
    # Training performance observation parameters
    eval_strategy="steps",  # Use "steps" to evaluate at specific intervals
    eval_steps=128,  # Evaluate every 128 steps
    save_strategy="steps",  # Save model checkpoint at specific intervals
    save_steps=128,  # Save model every 128 steps
    save_total_limit=100,  # Keep only 100 latest checkpoints
    load_best_model_at_end=True,  # Load the best model (based on eval_loss) after training
    metric_for_best_model="eval_loss",  # Metric to decide the best model
)


# Prepare evaluator
evaluator = EmbeddingSimilarityEvaluator(
    sentences1=[ex.texts[0] for ex in eval_set],
    sentences2=[ex.texts[1] for ex in eval_set],
    scores=[ex.label for ex in eval_set],
    main_similarity=SimilarityFunction.COSINE,
)

# Initialize the trainer
trainer = SentenceTransformerTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    loss=loss,
    args=args,
    evaluator=evaluator,
)

trainer.train()

model.save_pretrained("output/paraphrase-multilingual-MiniLM-L12-v2/final")
