import re
from datetime import datetime

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


