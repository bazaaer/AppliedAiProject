import pytest
import ollama as llm
# from deepeval import assert_test
# from deepeval.test_case import LLMTestCase
# from deepeval.metrics import AnswerRelevancyMetric

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


def test_create_models(client):
    """Test if models can be created successfully."""
    try:
        schrijfassistent_content = read_file_contents(SCHRIJFASSISTENT_MODELFILE)
        stijlassistent_content = read_file_contents(STIJLASSISTENT_MODELFILE)

        client.create(model='schrijfassistent', modelfile=schrijfassistent_content)
        client.create(model='stijlassistent', modelfile=stijlassistent_content)
    except Exception as e:
        pytest.fail(
            f"Model creation failed with error: {e}\n"
        )

# @pytest.mark.parametrize(
#     "test_case"
# )
# def test_customer_chatbot(test_case: LLMTestCase):
#     answer_relevancy_metric = AnswerRelevancyMetric()
#     assert_test(test_case, [answer_relevancy_metric])