import re

import pandas as pd
import spacy
from langdetect import DetectorFactory, detect

nlp = spacy.load("nl_core_news_lg")
spacy.prefer_gpu()

DetectorFactory.seed = 0


def load_data(filepath):
    """Extract: Load dataset from CSV file."""
    try:
        df = pd.read_csv(filepath)
        print("Dataset loaded successfully.")
        return df
    except FileNotFoundError:
        print("Error: Dataset file not found.")
        return pd.DataFrame()


def split_sentences(text):
    """Split text into sentences based on sentence boundary patterns."""
    sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    return re.split(sentence_pattern, text)


def is_important(sentence):
    """Identify important sentences based on entity presence, length, and parts of speech."""
    doc = nlp(sentence)
    return (
        len(doc.ents) > 0
        or 3 < len(doc) < 30
        or any(token.pos_ in {"PROPN", "NUM"} for token in doc)
    )


def is_dutch(text):
    """Detect if text is in Dutch."""
    try:
        return detect(text) == "nl"
    except:
        return False


def filter_and_transform(df):
    """Transform: Process sentences to extract, filter, and flag important Dutch sentences, with final cleanup."""
    keywords = [
        "browser",
        "menu",
        "contact",
        "2020 antwerpen",
        "sportcentrum",
        "bel",
        "surf",
        "ook interessant",
        "locatie",
        ":",
        "telefoneer",
        "schrijf",
        "website",
        "aanbod",
        "gezin",
        "euro",
        "mail",
        "tel+",
        "@",
        "€",
        "stadsplan",
        "leaflet",
        "gemeentearchief",
        "cookie",
        "NL",
        "internetbrowser",
        "E-mail",
        "©",
        "™",
    ]
    exclusion_pattern = "|".join(keywords)

    all_sentences = [
        sentence
        for text in df["body_content"].dropna()
        for sentence in split_sentences(text)
    ]
    sentences_df = pd.DataFrame(all_sentences, columns=["sentence"]).drop_duplicates()

    sentences_df["important"] = sentences_df["sentence"].apply(is_important)
    sentences_df = sentences_df[sentences_df["important"]].drop(columns="important")
    sentences_df["dutch"] = sentences_df["sentence"].apply(is_dutch)
    sentences_df = sentences_df[sentences_df["dutch"]].drop(columns="dutch")

    avg_length = sentences_df["sentence"].str.len().mean()
    filtered_df = sentences_df[
        (~sentences_df["sentence"].str.contains(exclusion_pattern, case=False))
        & (sentences_df["sentence"].str.len() >= avg_length - 18)
    ]

    filtered_df = filtered_df[
        ~(
            filtered_df["sentence"].str.contains(r"\|")
            & filtered_df["sentence"].str.contains("BE")
        )
    ]
    filtered_df["sentence"] = filtered_df["sentence"].apply(
        lambda x: f'"{x}"' if not x.startswith('"') and not x.endswith('"') else x
    )

    # Reset index for final DataFrame and set index name
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index.name = "index"

    return filtered_df


def export_data(df, filepath):
    """Load: Export the cleaned and filtered data to CSV."""
    df.to_csv(filepath, index=True)
    print("Processed data exported successfully.")


def etl_pipeline(input_filepath, output_filepath):
    """Run the full ETL process on the dataset."""
    df = load_data(input_filepath)
    if df.empty:
        return
    processed_df = filter_and_transform(df)
    export_data(processed_df, output_filepath)


# 'antwerpen.csv' is afkomstig van een elastic search op een aantal websites van stad antwerpen, waaronder:
# antwerpen.be;      visit.antwerpen.be;    job.antwerpen.be;
# pers.antwerpen.be; eloket.antwerpen.be;   magazine.antwerpen.be

etl_pipeline("antwerpen.csv", "important_sentences.csv")

pd.read_csv("important_sentences.csv").head()
