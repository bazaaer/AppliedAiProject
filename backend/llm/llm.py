import re
from datetime import datetime
import aiohttp
import json

import ollama

def client(host):
    """Fixture to set up the Ollama client."""
    return ollama.Client(host=host)


def read_file_contents(filepath):
    """Helper function to read and return the contents of a file."""
    try:
        with open(filepath, "r") as file:
            return file.read()
    except Exception as e:
        return f"Could not read file {filepath}: {e}"

# Precompile patterns
URL_PATTERN = re.compile(r"\b(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,}))\b")
DATE_PATTERN = re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b")
TIME_PATTERN = re.compile(r"\b(\d{1,2}):(\d{2})\s*uur\b")
ALPHANUMERIC_PATTERN = re.compile(r"""[^\w\s.,!?;:\\/*'"“”‘’„‟$€¥£₩₹₽₺₿™©<>&…=-]""")

def extract_and_replace_urls_and_dates(input_text: str) -> str:
    """
    Extracts and replaces URLs and dates in the input text.

    - URLs are normalized to include 'www.' if they do not already start with it.
    - Dates are converted to a more readable format ('D Month YYYY').

    Args:
        input_text (str): The text to process.

    Returns:
        str: The processed text with URLs and dates normalized.
    """
    url_pattern = URL_PATTERN
    date_pattern = DATE_PATTERN

    def replace_url(match: re.Match) -> str:
        domain = match.group(1)
        return f"www.{domain}" if not match.group(0).startswith("www.") else domain

    def replace_date(match: re.Match) -> str:
        day, month, year = match.groups()
        if len(year) == 2:  # Handle two-digit years
            year = "20" + year if int(year) < 50 else "19" + year
        try:
            # Parse the date into a datetime object
            date_obj = datetime.strptime(f"{int(day)}/{int(month)}/{year}", "%d/%m/%Y")
            # Format it as 'D Month YYYY' (no leading zeroes)
            return date_obj.strftime("%-d %B %Y").lower()
        except ValueError:
            return match.group(0)  # Return the original if parsing fails

    text = url_pattern.sub(replace_url, input_text)
    text = date_pattern.sub(replace_date, text)
    return text


def clean_and_normalize_text(input_text: str) -> str:
    """
    Cleans and normalizes the input text by removing special characters,
    formatting times, and sanitizing punctuation.

    - Replaces time formats 'HH:MM uur' with 'HH.MM uur'.
    - Removes non-alphanumeric characters except common punctuation and symbols.

    Args:
        input_text (str): The text to clean and normalize.

    Returns:
        str: The cleaned and normalized text.
    """
    time_pattern = TIME_PATTERN
    alphanumeric_pattern = ALPHANUMERIC_PATTERN

    def replace_time(match: re.Match) -> str:
        return match.group(0).replace(":", ".")

    text = time_pattern.sub(replace_time, input_text)
    return alphanumeric_pattern.sub("", text)


def process_text_before_rewriting(input_text: str) -> str:
    """
    Processes text by replacing URLs and dates before passing to LLM.

    Args:
        input_text (str): The text to process.

    Returns:
        str: The processed text.
    """
    return extract_and_replace_urls_and_dates(input_text)


def process_text_after_rewriting(input_text: str) -> str:
    """
    Processes text by cleaning up formatting and special characters after LLM.

    Args:
        input_text (str): The text to process.

    Returns:
        str: The cleaned text.
    """
    return clean_and_normalize_text(input_text)


async def write_sentence(
    session: aiohttp.ClientSession, 
    host: str, 
    text: str, 
    user_prompt: str = None
) -> str:
    # Preprocess the text
    text = process_text_before_rewriting(text)

    # Construct the prompt with optional user instruction
    prompt = f"{user_prompt}:\n\n{text}" if user_prompt else text

    async def fetch_response(model: str, prompt: str) -> str:
        """Helper function to call the API and process the NDJSON response."""
        async with session.post(
            f"{host}/api/generate",
            json={"model": model, "prompt": prompt}
        ) as response:
            if response.status != 200:
                raise ValueError(f"Failed to call '{model}': {response.status}")

            result = ""
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line:
                    try:
                        data = json.loads(line)
                        result += data.get("response", "")
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON from {model}: {line}. Error: {e}")
            return result

    # Process with the first model
    rewritten_response = await fetch_response("schrijfassistent", prompt)

    # Process with the second model
    styled_response = await fetch_response("stijlassistent", rewritten_response)

    # Postprocess the styled text
    output = process_text_after_rewriting(styled_response)
    return output
