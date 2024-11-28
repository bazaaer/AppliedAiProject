import pytest
from backend.checket.checker import SimilarityEvaluator
import torch
import os

EMBEDDINGS_PATH = "../checket/embeddings.pt"
RANDOM_EMBEDDINGS_PATH = "../checket/random_embeddings.pt"

@pytest.fixture
def random_embeddings_file():
    """
    Fixture to create a random embeddings file.
    """
    torch.manual_seed(42)  # Ensure deterministic random embeddings
    # Define the size of the embeddings (match real embeddings size for meaningful comparison)
    embedding_size = (1000, 768)  # Example size (1000 vectors, 768 dimensions)
    random_embeddings = torch.randn(embedding_size)

    # Save random embeddings to a .pt file
    torch.save(random_embeddings, RANDOM_EMBEDDINGS_PATH)

    yield RANDOM_EMBEDDINGS_PATH

    # Cleanup: Remove the file after the test
    if os.path.exists(RANDOM_EMBEDDINGS_PATH):
        os.remove(RANDOM_EMBEDDINGS_PATH)

@pytest.fixture
def similarity_evaluator():
    """
    Fixture to initialize the SimilarityEvaluator with mocked embeddings.
    """
    evaluator = SimilarityEvaluator(base_embeddings_path=EMBEDDINGS_PATH)
    return evaluator


def test_initialization(similarity_evaluator):
    """
    Test if the SimilarityEvaluator initializes correctly.
    """
    assert similarity_evaluator.model is not None, "Model should be loaded."
    assert similarity_evaluator.base_embeddings is not None, "Base embeddings should be loaded."

def test_similarity_score(similarity_evaluator):
    """
    Test the similarity score of a given sentence.
    """
    test_sentence = "This is a test sentence for similarity evaluation."
    k = 5

    score = similarity_evaluator.topk_mean_similarity_score(test_sentence, k)

    assert isinstance(score, float), "The similarity score should be a float."
    assert 0.0 <= score <= 1.0, "The similarity score should be between 0 and 1."

def test_special_characters(similarity_evaluator):

    score = similarity_evaluator.topk_mean_similarity_score("!@#$%^&*()")

    assert 0.0 <= score <= 1.0, "Similarity score should be between 0 and 1 for any input."

def test_k_larger_than_embeddings(similarity_evaluator):
    total_embeddings = similarity_evaluator.base_embeddings.size(0)
    sentence = "Test sentence for large k."
    k = total_embeddings + 10

    with pytest.raises(RuntimeError, match="selected index k out of range"):
        similarity_evaluator.topk_mean_similarity_score(sentence, k=k)

def test_similarity_ranking_dutch_english(similarity_evaluator):
    sentence1 = "Lees zorgvuldig de details van het reglement en de voorwaarden voordat je een premieaanvraag doet."
    sentence2 = "Carefully read the details of the rules and conditions before applying for a premium."

    tolerance = 0.2

    score1 = similarity_evaluator.topk_mean_similarity_score(sentence1)
    score2 = similarity_evaluator.topk_mean_similarity_score(sentence2)
    assert abs(score1 - score2) <= tolerance, \
        f"Scores should be within {tolerance} but got {score1} and {score2}."

def test_similarity_ranking_dutch_french(similarity_evaluator):
    sentence1 = "Lees zorgvuldig de details van het reglement en de voorwaarden voordat je een premieaanvraag doet."
    sentence2 = "Lisez attentivement les détails du règlement et des conditions avant de demander une prime."

    tolerance = 0.2

    score1 = similarity_evaluator.topk_mean_similarity_score(sentence1)
    score2 = similarity_evaluator.topk_mean_similarity_score(sentence2)
    assert abs(score1 - score2) <= tolerance, \
        f"Scores should be within {tolerance} but got {score1} and {score2}."

def test_similarity_dutch(similarity_evaluator):
    sentence1 = "Lees zorgvuldig de details van het reglement en de voorwaarden voordat je een premieaanvraag doet."
    sentence2 = "Antwerpen presenteert zijn plan voor digitale verandering."

    tolerance = 0.2

    score1 = similarity_evaluator.topk_mean_similarity_score(sentence1)
    score2 = similarity_evaluator.topk_mean_similarity_score(sentence2)
    assert abs(score1 - score2) <= tolerance, \
        f"Scores should be within {tolerance} but got {score1} and {score2}."

def test_stress(similarity_evaluator):
    sentence = "Antwerpen presenteert zijn plan voor digitale verandering."
    expected_score = None
    for _ in range(1000):
        score = similarity_evaluator.topk_mean_similarity_score(sentence)
        assert 0.0 <= score <= 1.0, "Score should remain valid under stress."
        if expected_score is None:
            expected_score = score
        assert score == expected_score, "Score should remain the same under stress."


def test_real_vs_saved_random_embeddings(random_embeddings_file):
    """
    Test to compare similarity scores using real embeddings versus saved random embeddings.
    """
    evaluator_with_real_embeddings = SimilarityEvaluator(base_embeddings_path=EMBEDDINGS_PATH)

    evaluator_with_random_embeddings = SimilarityEvaluator(base_embeddings_path=random_embeddings_file)

    test_sentence = "This is a test sentence for similarity evaluation."
    k = 5

    real_score = evaluator_with_real_embeddings.topk_mean_similarity_score(test_sentence, k)
    random_score = evaluator_with_random_embeddings.topk_mean_similarity_score(test_sentence, k)

    # Compare scores
    print(f"\nSimilarity score with real embeddings: {real_score}")
    print(f"Similarity score with random embeddings: {random_score}")

    assert real_score != random_score, "Scores should differ between real and random embeddings."
    assert 0.0 <= real_score <= 1.0, "Real embeddings score should be valid."
    assert 0.0 <= random_score <= 1.0, "Random embeddings score should be valid."