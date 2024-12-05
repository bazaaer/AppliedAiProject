import pandas as pd

# Load the dataset
df = pd.read_csv('../training.csv')

# Clean `sentence2` where its length is more than 1.5 times the length of `sentence1`
df = df[
    ~(
        (df['score'] >= 0.5) &
        (df['sentence2'].str.len() > df['sentence1'].str.len() * 2)
    )
]

# Surround `sentence2` with double quotes if not already enclosed
df['sentence2'] = df['sentence2'].apply(
    lambda x: f'"{x}"' if not (x.startswith('"') and x.endswith('"')) else x
)

# Save the cleaned dataset to a new CSV
df.to_csv('cleaned_training.csv', index=False)