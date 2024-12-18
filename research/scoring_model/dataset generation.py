import datetime
import os
import re
import traceback

import ollama
import pandas as pd


def read_file_contents(filepath):
    """Helper function to read and return the contents of a file."""
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file {filepath} not found.")
        with open(filepath, "r") as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Could not read file {filepath}: {e}")


def save_partial_data(processed_sentences, filename="training.csv"):
    """Saves the processed sentences to a CSV file, appending if the file exists."""
    df = pd.DataFrame(processed_sentences)
    save_df_to_csv(df, filename)


def save_df_to_csv(df: pd.DataFrame, filename: str = "training.csv"):
    """Save DataFrame to CSV, appending if file already exists."""
    file_exists = os.path.exists(filename)
    df.to_csv(filename, mode='a', header=not file_exists, index=False)


def extract_and_replace_urls_and_dates(input_text: str) -> str:
    """Extracts and replaces URLs and dates in the input text."""
    url_pattern = re.compile(
        r"\b(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,}))\b"
    )
    date_pattern = re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b")

    def replace_url(match: re.Match) -> str:
        domain = match.group(1)
        return f"www.{domain}" if not match.group(0).startswith("www.") else domain

    def replace_date(match: re.Match) -> str:
        day, month, year = match.groups()
        if len(year) == 2:  # Handle two-digit years
            year = "20" + year if int(year) < 50 else "19" + year
        try:
            # Parse the date into a datetime object
            date_obj = datetime.datetime.strptime(f"{int(day)}/{int(month)}/{year}", "%d/%m/%Y")
            # Format it as 'D Month YYYY' (no leading zeroes)
            return date_obj.strftime("%-d %B %Y").lower()
        except ValueError:
            return match.group(0)  # Return the original if parsing fails

    text = url_pattern.sub(replace_url, input_text)
    text = date_pattern.sub(replace_date, text)
    return text


def clean_and_normalize_text(input_text: str) -> str:
    """Cleans and normalizes the input text by removing special characters."""
    time_pattern = re.compile(r"\b(\d{1,2}):(\d{2})\s*uur\b")
    alphanumeric_pattern = re.compile(
        r"""[^\w\s.,!?;:\\/*'`´"‘’„‟“”$€¥£₩₹₽₺₿™©<>&…=-]"""
    )

    def replace_time(match: re.Match) -> str:
        return match.group(0).replace(":", ".")

    text = time_pattern.sub(replace_time, input_text)
    return alphanumeric_pattern.sub("", text)


def process_text_before_rewriting(input_text: str) -> str:
    """Processes text by replacing URLs and dates before passing to LLM."""
    return extract_and_replace_urls_and_dates(input_text)


def process_text_after_rewriting(input_text: str) -> str:
    """Cleans up formatting and special characters after LLM."""
    return clean_and_normalize_text(input_text)


def write_sentence(sentence: str, writing_llm: str, style_llm: str) -> str:
    """Generates responses using the LLM client with text cleaning and normalization."""
    rewritten_response = ollama.generate(
        model=writing_llm,
        prompt=f"""Pas de schrijf regels toe op deze zin: {sentence}"""
    )

    style_response = ollama.generate(
        model=style_llm,
        prompt=f"""Pas de stijlregels toe op deze zin: {rewritten_response['response']}""",
    )

    return style_response['response']


def main():
    df = pd.read_csv("important_sentences.csv", index_col=0)
    df.rename(columns={"sentence": "sentence1"}, inplace=True)
    df = df.sample(n=len(df) // 2, random_state=42)

    processed_sentences = []  # Initialize an empty list to store processed sentences
    batch_size = 1000  # Save after every 1,000 entries
    batch_counter = 1  # Counter to track the batch number

    try:
        for idx, row in df.iterrows():
            original_sentence = row["sentence1"]

            processed_sentence = process_text_before_rewriting(original_sentence)
            sentence_rewrite = write_sentence(
                sentence=processed_sentence,
                writing_llm="schrijfassistent_goed",
                style_llm="stijlassistent_goed"
            )
            sentence_good_rewrite = process_text_after_rewriting(sentence_rewrite)
            processed_sentences.append(
                {
                    "sentence1": original_sentence,
                    "sentence2": sentence_good_rewrite,
                    "score": 1.0,
                }
            )

            sentence_half_rewrite = write_sentence(
                sentence=original_sentence,
                writing_llm="schrijfassistent_half",
                style_llm="stijlassistent_half"
            )
            processed_sentences.append(
                {
                    "sentence1": original_sentence,
                    "sentence2": sentence_half_rewrite,
                    "score": 0.5,
                }
            )

            sentence_bad_rewrite = write_sentence(
                sentence=original_sentence,
                writing_llm="schrijfassistent_slecht",
                style_llm="stijlassistent_slecht"
            )
            processed_sentences.append(
                {
                    "sentence1": original_sentence,
                    "sentence2": sentence_bad_rewrite,
                    "score": 0.0,
                }
            )

            # Save partial data after every 1000 sentences
            if len(processed_sentences) >= batch_size:
                save_partial_data(processed_sentences)
                processed_sentences = []  # Reset the list for the next batch
                batch_counter += 1

        # Save remaining data after loop finishes
        if processed_sentences:
            save_partial_data(processed_sentences)

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()  # Print full traceback for debugging
        if processed_sentences:
            save_partial_data(processed_sentences)


if __name__ == "__main__":
    # Define the file paths for the model files
    model_files = {
        "schrijfassistent_goed": "Modelfile_schrijfassistent_goed",
        "stijlassistent_goed": "Modelfile_stijlassistent_goed",
        "schrijfassistent_half": "Modelfile_schrijfassistent_half",
        "stijlassistent_half": "Modelfile_stijlassistent_half",
        "schrijfassistent_slecht": "Modelfile_schrijfassistent_slecht",
        "stijlassistent_slecht": "Modelfile_stijlassistent_slecht",
    }

    # Read model files and create models
    for model_name, file_path in model_files.items():
        model_content = read_file_contents(file_path)
        ollama.create(model=model_name, modelfile=model_content)

    main()
