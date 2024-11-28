import pytest
import spacy
from backend.checket.grouper import SentenceGrouper  # Update with actual module import
import re


@pytest.fixture
def grouper():
    return SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.72)


def test_group_consecutive_similar_sentences(grouper):
    text = "De appel valt van de boom. de appel is groen."

    # Test that these two sentences are grouped together
    grouped_sentences = grouper.group_consecutive_similar_sentences(text)

    # There should be one group because both sentences are similar
    assert len(grouped_sentences) == 1
    grouped_text, group_idx = grouped_sentences[0]
    assert grouped_text == "De appel valt van de boom. de appel is groen."
    assert group_idx == 0  # The group index should be 0


def test_group_and_rejoin_sentences(grouper):
    text = "De appel valt van de boom. de appel is groen. de zon schijnt. het is een mooie dag."

    # Group the sentences first
    grouped_sentences = grouper.group_consecutive_similar_sentences(text)

    # Now, ungroup them by concatenating the sentences back
    ungrouped_text = " ".join([grouped_text for grouped_text, _ in grouped_sentences])

    # Assert the text is the same after rejoining
    assert ungrouped_text.strip() == text.strip()


def test_group_with_html_tags(grouper):
    text = "De appel valt van de boom <strong>de appel is groen.</strong> De zon schijnt."

    # Test that sentences with HTML tags are grouped correctly
    grouped_sentences = grouper.group_consecutive_similar_sentences(text)

    grouped_text, group_idx = grouped_sentences[0]

    # Assert the HTML tag is handled correctly and the sentences are grouped
    assert "<strong>" in grouped_text and "</strong>" in grouped_text
    assert "De appel valt van de boom" in grouped_text
    assert "de appel is groen" in grouped_text
    assert group_idx == 0


def test_no_valid_embeddings(grouper):
    text = " "  # Empty text should raise an error since there are no valid sentences
    with pytest.raises(ValueError, match="No valid sentence embeddings found in the provided text."):
        grouper.group_consecutive_similar_sentences(text)

