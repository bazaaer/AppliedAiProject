import pytest
import ollama as llm
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
import re

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


def clean_and_process_text(input_text):
    url_pattern = re.compile(r'\b(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,}))\b')
    time_pattern = re.compile(r'\b(\d{1,2}):(\d{2})\s*uur\b')
    alphanumeric_pattern = re.compile(r"""[^\w\s.,!?;:\\/*'"“”‘’„‟$€¥£₩₹₽₺₿™©<>&…=-]""")

    def replace_url(match):
        domain = match.group(1)
        return f"www.{domain}" if not match.group(0).startswith('www.') else domain

    def replace_time(match):
        return match.group(0).replace(':', '.')

    def process_text(text):
        text = url_pattern.sub(replace_url, text)
        text = time_pattern.sub(replace_time, text)
        return alphanumeric_pattern.sub('', text)

    return process_text(input_text)


def write_sentence(client, sentence) -> str:
    """Generates responses using the LLM client."""
    rewritten_response = client.generate(model='schrijfassistent', prompt=sentence)
    style_response = client.generate(model='stijlassistent', prompt=rewritten_response['response'])
    output = clean_and_process_text(style_response['response'])
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
    dataset = EvaluationDataset(test_cases=[
        LLMTestCase(
            input="Het is onze bedoeling om in de toekomst initiatieven te nemen die bijdragen aan het vergroten van de veiligheid in onze buurten.",
            actual_output=write_sentence(client, "Het is onze bedoeling om in de toekomst initiatieven te nemen die bijdragen aan het vergroten van de veiligheid in onze buurten."),
            expected_output="We werken aan veiligere buurten."
        ),
        LLMTestCase(
            input="Het bedrijf is gericht op duurzame oplossingen voor toekomstige generaties.",
            actual_output=write_sentence(client, "Het bedrijf is gericht op duurzame oplossingen voor toekomstige generaties."),
            expected_output="We ontwikkelen duurzame oplossingen voor de toekomst."
        )
    ])
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.75, model="gpt-4o-mini")
    evaluate(dataset, metrics=[answer_relevancy_metric])

def test_llm_hour_notation(client):
    """Test LLM's ability to rewrite hour notations."""
    dataset = EvaluationDataset(test_cases=[
        LLMTestCase(
            input="De workshop vindt plaats 1/12/2024 om 10:00 u.",
            actual_output=write_sentence(client, "De workshop vindt plaats 1/12/2024 om 10:00 u."),
            expected_output="De workshop vindt plaats 1 december 2024 om 10.00 uur."
        ),
        LLMTestCase(
            input="De vergadering begint om 15:30 u.",
            actual_output=write_sentence(client, "De vergadering begint om 15:30 u."),
            expected_output="De vergadering begint om 15.30 uur."
        )
    ])
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.95, model="gpt-4o-mini", strict_mode=True)
    evaluate(dataset, metrics=[answer_relevancy_metric])

def test_llm_valuta_notation(client):
    """Test LLM's ability to rewrite monetary values."""
    dataset = EvaluationDataset(test_cases=[
        LLMTestCase(
            input="Het totaal plaatje kost €5.",
            actual_output=write_sentence(client, "Het totaal plaatje kost €5."),
            expected_output="Het totaal plaatje kost 5 euro."
        ),
        LLMTestCase(
            input="De prijs is €19,99 per persoon.",
            actual_output=write_sentence(client, "De prijs is €19,99 per persoon."),
            expected_output="De prijs is 19,99 euro per persoon."
        )
    ])
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.95, model="gpt-4o-mini", strict_mode=True)
    evaluate(dataset, metrics=[answer_relevancy_metric])

def test_llm_date_notation(client):
    """Test LLM's ability to rewrite date formats."""
    dataset = EvaluationDataset(test_cases=[
        LLMTestCase(
            input="De workshop vindt plaats op 1/12/2024.",
            actual_output=write_sentence(client, "De workshop vindt plaats op 1/12/2024."),
            expected_output="De workshop vindt plaats op 1 december 2024."
        ),
        LLMTestCase(
            input="De afspraak is op 25/3/2023.",
            actual_output=write_sentence(client, "De afspraak is op 25/3/2023."),
            expected_output="De afspraak is op 25 maart 2023."
        )
    ])
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.95, model="gpt-4o-mini", strict_mode=True)
    evaluate(dataset, metrics=[answer_relevancy_metric])

def test_llm_spellcheck(client):
    """Test LLM's ability to rewrite date formats."""
    dataset = EvaluationDataset(test_cases=[
        LLMTestCase(
            input="De hond loopt los in de park.",
            actual_output=write_sentence(client, "De hond loopt los in de park."),
            expected_output="De hond loopt los in het park."
        ),
        LLMTestCase(
            input="Ik heb geen ide wat je bedoelt.",
            actual_output=write_sentence(client, "Ik heb geen ide wat je bedoelt."),
            expected_output="Ik heb geen idee wat je bedoelt."
        )
    ])
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.95, model="gpt-4o-mini", strict_mode=True)
    evaluate(dataset, metrics=[answer_relevancy_metric])

def test_llm_html_layout(client):
    """Test LLM's ability to rewrite date formats."""
    dataset = EvaluationDataset(test_cases=[
        LLMTestCase(
            input="De <strong>appel</strong> is groen",
            actual_output=write_sentence(client, "De <strong>appel</strong> is groen"),
            expected_output="De <strong>appel</strong> is groen"
        )
    ])
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=1.0, model="gpt-4o-mini", strict_mode=True)
    evaluate(dataset, metrics=[answer_relevancy_metric])