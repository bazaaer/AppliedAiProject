import re
from datetime import datetime
from typing import Callable

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

import ollama as llm

SCHRIJFASSISTENT_MODELFILE = "../checket/Modelfile_schrijfassistent"
STIJLASSISTENT_MODELFILE = "../checket/Modelfile_stijlassistent"
HOST = "http://localhost:11435"

@pytest.fixture
def client():
    """Fixture to set up the Ollama client."""
    return llm.Client(host=HOST)


def read_file_contents(filepath):
    """Helper function to read and return the contents of a file."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        pytest.fail(f"Could not read file {filepath}: {e}")


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
    url_pattern = re.compile(r'\b(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,}))\b')
    date_pattern = re.compile(r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b')

    def replace_url(match: re.Match) -> str:
        domain = match.group(1)
        return f"www.{domain}" if not match.group(0).startswith('www.') else domain

    def replace_date(match: re.Match) -> str:
        day, month, year = match.groups()
        if len(year) == 2:  # Handle two-digit years
            year = '20' + year if int(year) < 50 else '19' + year
        try:
            # Parse the date into a datetime object
            date_obj = datetime.strptime(f"{int(day)}/{int(month)}/{year}", '%d/%m/%Y')
            # Format it as 'D Month YYYY' (no leading zeroes)
            return date_obj.strftime('%-d %B %Y').lower()
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
    time_pattern = re.compile(r'\b(\d{1,2}):(\d{2})\s*uur\b')
    alphanumeric_pattern = re.compile(r"""[^\w\s.,!?;:\\/*'"“”‘’„‟$€¥£₩₹₽₺₿™©<>&…=-]""")

    def replace_time(match: re.Match) -> str:
        return match.group(0).replace(':', '.')

    text = time_pattern.sub(replace_time, input_text)
    return alphanumeric_pattern.sub('', text)


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


def write_sentence(client: Callable, sentence: str) -> str:
    """
    Generates responses using the LLM client with text cleaning and normalization.

    - Cleans and processes text before and after LLM rewriting.

    Args:
        client (Callable): A client function for generating responses.
        sentence (str): The input sentence.

    Returns:
        str: The final processed and normalized output.
    """
    sentence = process_text_before_rewriting(sentence)

    rewritten_response = client.generate(model='schrijfassistent', prompt=sentence)

    style_response = client.generate(model='stijlassistent', prompt=rewritten_response['response'])

    output = process_text_after_rewriting(style_response['response'])
    return output


def test_create_models(client):
    """Test if models can be created successfully."""
    try:
        schrijfassistent_content = read_file_contents(SCHRIJFASSISTENT_MODELFILE)
        stijlassistent_content = read_file_contents(STIJLASSISTENT_MODELFILE)

        client.create(model='schrijfassistent', modelfile=schrijfassistent_content)
        client.create(model='stijlassistent', modelfile=stijlassistent_content)
    except Exception as e:
        pytest.fail(f"Model creation failed with error: {e}")


def test_llm_rewriting(client):
    """Test LLM's rewriting abilities."""
    try:
        testcase = LLMTestCase(
            input="Het is onze bedoeling om in de toekomst initiatieven te nemen die bijdragen aan het vergroten van de veiligheid in onze buurten.",
            actual_output=write_sentence(client,
                                         "Het is onze bedoeling om in de toekomst initiatieven te nemen die bijdragen aan het vergroten van de veiligheid in onze buurten."),
            expected_output="We werken aan veiligere buurten."
        )
        answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.75, model="gpt-4o-mini")
        assert_test(testcase, metrics=[answer_relevancy_metric])
    except Exception as e:
        if "Limit Reached" in str(e):
            print("Warning: Test limit reached. Continuing without failing.")
        else:
            raise


def test_llm_hour_notation(client):
    """Test LLM's ability to rewrite hour notations."""
    try:

        testcase = LLMTestCase(
            input="De workshop vindt plaats om 10:00 u.",
            actual_output=write_sentence(client, "De workshop vindt plaats om 10:00 u."),
            expected_output="De workshop vindt plaats om 10.00 uur."
        )
        answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.95, model="gpt-4o-mini", strict_mode=True)
        assert_test(testcase, metrics=[answer_relevancy_metric])
    except Exception as e:
        if "Limit Reached" in str(e):
            print("Warning: Test limit reached. Continuing without failing.")
        else:
            raise


def test_llm_valuta_notation(client):
    """Test LLM's ability to rewrite monetary values."""
    try:

        testcase = LLMTestCase(
            input="Het totaal plaatje kost €5.",
            actual_output=write_sentence(client, "Het totaal plaatje kost €5."),
            expected_output="Het totaal plaatje kost 5 euro."
        )
        answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.95, model="gpt-4o-mini", strict_mode=True)
        assert_test(testcase, metrics=[answer_relevancy_metric])
    except Exception as e:
        if "Limit Reached" in str(e):
            print("Warning: Test limit reached. Continuing without failing.")
        else:
            raise


def test_llm_date_notation(client):
    """Test LLM's ability to rewrite date formats."""
    try:
        testcase = LLMTestCase(
            input="De workshop vindt plaats op 1/12/2024.",
            actual_output=write_sentence(client, "De workshop vindt plaats op 1/12/2024."),
            expected_output="De workshop vindt plaats op 01 december 2024."
        )
        answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.45, model="gpt-4o-mini")
        assert_test(testcase, metrics=[answer_relevancy_metric])
    except Exception as e:
        if "Limit Reached" in str(e):
            print("Warning: Test limit reached. Continuing without failing.")
        else:
            raise


def test_llm_spellcheck(client):
    """Test LLM's ability to rewrite date formats."""
    try:
        testcase = LLMTestCase(
            input="De hond loopt los in de park.",
            actual_output=write_sentence(client, "De hond loopt los in de park."),
            expected_output="De hond loopt los in het park."
        )
        answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.95, model="gpt-4o-mini", strict_mode=True)
        assert_test(testcase, metrics=[answer_relevancy_metric])
    except Exception as e:
        if "Limit Reached" in str(e):
            print("Warning: Test limit reached. Continuing without failing.")
        else:
            raise


def test_llm_html_layout(client):
    """Test LLM's ability to rewrite date formats."""
    try:
        testcase = LLMTestCase(
            input="<a href='https://www.example.com'>Klik hier voor meer informatie</a>.",
            actual_output=write_sentence(client, "<a href='https://www.example.com'>Klik hier voor meer informatie</a>."),
            expected_output="<a href='www.example.com'>Klik hier voor meer informatie</a>."
        )
        answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.85, model="gpt-4o-mini", strict_mode=True)
        html_correctness_metric = GEval(
            name="HTML Correctness",
            criteria="Determine whether the actual output includes the same html tags based on the expected output.",
            model="gpt-4o-mini",
            threshold=0.5,
            evaluation_steps=[
                "Check whether the HTML-tags in 'expected output' are also in the 'actual output'",
                "You should heavily penalize omission of HTML tags"
            ],
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ]
        )
        assert_test(testcase, metrics=[answer_relevancy_metric, html_correctness_metric])
    except Exception as e:
        if "Limit Reached" in str(e):
            print("Warning: Test limit reached. Continuing without failing.")
        else:
            raise
