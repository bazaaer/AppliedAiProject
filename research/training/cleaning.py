import pandas as pd

# Load the dataset
df = pd.read_csv('training.csv')

# Clean `sentence2` where its length is more than 1.5 times the length of `sentence1`
df['sentence2'] = df.apply(
    lambda row: row['sentence2'][:round(len(row['sentence1']) * 1.5)]
    if len(row['sentence2']) > round(len(row['sentence1']) * 1.5) else row['sentence2'], axis=1
)

# Remove rows where `sentence2` contains more than one newline character
df = df[df['sentence2'].str.count('\n') <= 1]

# Surround `sentence2` with double quotes if not already enclosed
df['sentence2'] = df['sentence2'].apply(
    lambda x: f'"{x}"' if not (x.startswith('"') and x.endswith('"')) else x
)

df['score'] = df['score'].replace(0.5, 0.9)

# Save the cleaned dataset to a new CSV
df.to_csv('cleaned_training.csv', index=False)