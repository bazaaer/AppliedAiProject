import pytest

from backend.checket.grouper import SentenceGrouper


@pytest.fixture
def grouper():
    return SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.72)


def test_group_consecutive_similar_sentences(grouper):
    text = "De appel valt van de boom. de appel is groen."

    grouped_sentences = grouper.group_consecutive_similar_sentences(text)

    assert len(grouped_sentences) == 1
    grouped_text, group_idx = grouped_sentences[0]
    assert grouped_text == "De appel valt van de boom. de appel is groen."
    assert group_idx == 0


def test_group_and_rejoin_sentences(grouper):
    text = "De appel valt van de boom. de appel is groen. de zon schijnt. het is een mooie dag."

    grouped_sentences = grouper.group_consecutive_similar_sentences(text)

    ungrouped_text = " ".join([grouped_text for grouped_text, _ in grouped_sentences])

    assert ungrouped_text.strip() == text.strip()


def test_group_with_html_tags(grouper):
    text = (
        "De appel valt van de boom <strong>de appel is groen.</strong> De zon schijnt."
    )

    grouped_sentences = grouper.group_consecutive_similar_sentences(text)

    grouped_text, group_idx = grouped_sentences[0]

    assert "<strong>" in grouped_text and "</strong>" in grouped_text
    assert "De appel valt van de boom" in grouped_text
    assert "de appel is groen" in grouped_text
    assert group_idx == 0


def test_no_valid_embeddings(grouper):
    text = " "
    with pytest.raises(
        ValueError, match="No valid sentence embeddings found in the provided text."
    ):
        grouper.group_consecutive_similar_sentences(text)
