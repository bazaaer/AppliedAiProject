import os

import pytest
import torch

from backend.checket.checker import SimilarityEvaluator

EMBEDDINGS_PATH = "../checket/embeddings.pt"
RANDOM_EMBEDDINGS_PATH = "../checket/random_embeddings.pt"


@pytest.fixture
def random_embeddings_file():
    """
    Fixture to create a random embeddings file.
    """
    torch.manual_seed(42)  # Ensure deterministic random embeddings
    embedding_size = (1000, 768)
    random_embeddings = torch.randn(embedding_size)

    torch.save(random_embeddings, RANDOM_EMBEDDINGS_PATH)

    yield RANDOM_EMBEDDINGS_PATH

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
    assert (
        similarity_evaluator.base_embeddings is not None
    ), "Base embeddings should be loaded."


def test_functionality(similarity_evaluator):
    """
    It should test if a similarity score is given,
    if not, the loaded model doesn't support similarity scoring in the checker.py file
    """
    test_sentence = "This is a test sentence for similarity evaluation."
    k = 5

    score = similarity_evaluator.topk_mean_similarity_score(test_sentence, k)

    assert isinstance(score, float), "The similarity score should be a float."
    assert 0.0 <= score <= 1.0, "The similarity score should be between 0 and 1."


def test_special_characters(similarity_evaluator):
    """
    Special characters should still give a similarity score between 0 and 1
    but not above 0.8 since it's not a good sentence.
    """
    score = similarity_evaluator.topk_mean_similarity_score("!@#$%^&*()")

    assert (
        0.0 <= score <= 1.0
    ), "Similarity score should be between 0 and 1 for any input."
    assert (
        score <= 0.8
    ), "Similarity score shouldn't be above 0.8 meaning since it isn't a well written sentence."


def test_k_larger_than_embeddings(similarity_evaluator):
    """
    This should give an error.
    """
    total_embeddings = similarity_evaluator.base_embeddings.size(0)
    sentence = "Test sentence for large k."
    k = total_embeddings + 10

    with pytest.raises(RuntimeError, match="selected index k out of range"):
        similarity_evaluator.topk_mean_similarity_score(sentence, k=k)


def test_similarity_ranking_dutch_english(similarity_evaluator):
    """
    The scoring model is designed to support multiple languages (multilingual).
    However, since the training data does not include English, its performance in English may not be optimal.
    To account for this, a higher tolerance threshold is used for English inputs.
    This test evaluates the model's multilingual capabilities using both Dutch and English inputs.
    """
    sentence1 = "Lees zorgvuldig de details van het reglement en de voorwaarden voordat je een premieaanvraag doet."
    sentence2 = "Carefully read the details of the rules and conditions before applying for a premium."

    tolerance = 0.2

    score1 = similarity_evaluator.topk_mean_similarity_score(sentence1)
    score2 = similarity_evaluator.topk_mean_similarity_score(sentence2)
    print(f"\nDutch: {score1} and English: {score2}.")
    assert (
        abs(score1 - score2) <= tolerance
    ), f"Scores should be within {tolerance} but got {score1} and {score2}."


def test_similarity_ranking_dutch_french(similarity_evaluator):
    """
    The scoring model is designed to support multiple languages (multilingual).
    However, since the training data does not include French, its performance in French may not be optimal.
    To account for this, a higher tolerance threshold is used for French inputs.
    This test evaluates the model's multilingual capabilities using both Dutch and French inputs.
    """
    sentence1 = "Lees zorgvuldig de details van het reglement en de voorwaarden voordat je een premieaanvraag doet."
    sentence2 = "Lisez attentivement les détails du règlement et des conditions avant de demander une prime."

    tolerance = 0.2

    score1 = similarity_evaluator.topk_mean_similarity_score(sentence1)
    score2 = similarity_evaluator.topk_mean_similarity_score(sentence2)
    print(f"\nDutch: {score1} and French: {score2}.")
    assert (
        abs(score1 - score2) <= tolerance
    ), f"Scores should be within {tolerance} but got {score1} and {score2}."


def test_similarity_dutch(similarity_evaluator):
    """
    Tests if the score of new unseen sentences are above 0.8 and similar when compared to eachother.
    If A is a good sentence and B is a good sentence both should be above 0.8 and around the same score.
    """
    # These are unseen sentences from the pers.antwerpen.be website.
    sentence1 = "Door enkele eenvoudige vragen te beantwoorden, krijgen Antwerpenaren de specifieke boomsoorten voorgesteld die de meeste kansen hebben om op hun perceel volwaardig uit te groeien."
    sentence2 = "Daarnaast overschreed de ruimte van de rookkamer in sommige shishabars ook de maximaal toegestane oppervlakte van 25% van de totale oppervlakte."

    tolerance = 0.1

    score1 = similarity_evaluator.topk_mean_similarity_score(sentence1)
    score2 = similarity_evaluator.topk_mean_similarity_score(sentence2)
    assert (
        abs(score1 - score2) <= tolerance
    ), f"Scores should be within {tolerance} but got {score1} and {score2}."
    assert 0.8 <= score1, f"Score should be above 0.8 but got {score1} instead."
    assert 0.8 <= score2, f"Score should be above 0.8 but got {score2} instead."


def test_stress(similarity_evaluator):
    """
    The scores should not vary when stress tested, if they do the model has a built-in randomness.
    """
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
    If a random score is more than a real embedding your embeddings file is either very small or consists of bad data.
    Look at the research directory in the ai-research branch of klopta on github!
    """
    evaluator_with_real_embeddings = SimilarityEvaluator(
        base_embeddings_path=EMBEDDINGS_PATH
    )

    evaluator_with_random_embeddings = SimilarityEvaluator(
        base_embeddings_path=random_embeddings_file
    )

    test_sentence = "This is a test sentence for similarity evaluation."
    k = 5

    real_score = evaluator_with_real_embeddings.topk_mean_similarity_score(
        test_sentence, k
    )
    random_score = evaluator_with_random_embeddings.topk_mean_similarity_score(
        test_sentence, k
    )

    print(f"\nSimilarity score with real embeddings: {real_score}")
    print(f"Similarity score with random embeddings: {random_score}")

    assert (
        real_score != random_score
    ), "Scores should differ between real and random embeddings."
    assert 0.0 <= real_score <= 1.0, "Real embeddings score should be valid."
    assert 0.0 <= random_score <= 1.0, "Random embeddings score should be valid."
