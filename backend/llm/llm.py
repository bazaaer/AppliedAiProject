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


async def write_sentence(session: aiohttp.ClientSession, host: str, sentence: str) -> str:
    """
    Generates responses using the LLM client with text cleaning and normalization.

    Args:
        session (aiohttp.ClientSession): The shared aiohttp session for HTTP requests.
        host (str): The base URL for the Ollama client.
        sentence (str): The input sentence.

    Returns:
        str: The final processed and normalized output.
    """
    sentence = process_text_before_rewriting(sentence)

    # Send the first request to "schrijfassistent"
    async with session.post(
        f"{host}/api/generate",
        json={"model": "schrijfassistent", "prompt": sentence}
    ) as response:
        if response.status != 200:
            raise ValueError(f"Failed to call 'schrijfassistent': {response.status}")
        
        # Read the NDJSON response line by line
        rewritten_response = ""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line:  # Avoid empty lines
                data = json.loads(line)
                rewritten_response += data.get("response", "")

    # Send the second request to "stijlassistent"
    async with session.post(
        f"{host}/api/generate",
        json={"model": "stijlassistent", "prompt": rewritten_response}
    ) as response:
        if response.status != 200:
            raise ValueError(f"Failed to call 'stijlassistent': {response.status}")

        # Read the NDJSON response line by line
        styled_response = ""
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if line:  # Avoid empty lines
                data = json.loads(line)
                styled_response += data.get("response", "")

    output = process_text_after_rewriting(styled_response)
    return output
