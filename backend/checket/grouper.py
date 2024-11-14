import spacy
import cupy as cp
from typing import List, Tuple

class SentenceGrouper:
    """
    A class for grouping consecutive, semantically similar sentences from text based on cosine similarity.

    This class leverages SpaCy for sentence tokenization and embedding generation, with GPU acceleration
    via CuPy for efficient cosine similarity calculations. Sentences are grouped together when their similarity
    score meets a specified threshold.

    Parameters:
    - model (str): The SpaCy model to load for language processing (default: "nl_core_news_md").
    - similarity_threshold (float): The minimum cosine similarity score required for sentences to be grouped (default: 0.75).

    Methods:
    - group_consecutive_similar_sentences(text: str) -> List[Tuple[str, int]]:
        Groups consecutive sentences in the input text by semantic similarity. Each sentence group is returned
        as a tuple containing the grouped text and its associated group index. Sentences that lack valid embeddings
        (e.g., empty or link-only sentences) are marked with an index of -1, preserving the original sentence order
        within the output. Raises a ValueError if an empty string is provided as input.
    """
    def __init__(self, model: str = "nl_core_news_md", similarity_threshold: float = 0.75):
        self.nlp = spacy.load(model)
        spacy.prefer_gpu()
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def _compute_cosine_similarity(x: cp.ndarray, y: cp.ndarray = None) -> cp.ndarray:
        if y is None:
            y = x

        x = cp.asarray(x)
        y = cp.asarray(y)

        dot_product = cp.dot(x, y.T)
        norm_x = cp.linalg.norm(x, axis=1, keepdims=True)
        norm_y = cp.linalg.norm(y, axis=1, keepdims=True)

        cosine_similarity = dot_product / (norm_x * norm_y.T)
        return cosine_similarity

    def group_consecutive_similar_sentences(self, text: str) -> List[Tuple[str, int]]:
        doc = self.nlp(text)

        valid_sentences = []
        valid_embeddings = []
        invalid_sentences = []

        for sent in doc.sents:
            sentence_text = sent.text.strip()
            if sentence_text:
                embedding = cp.array(sent.vector)
                if not cp.all(embedding == 0):
                    valid_sentences.append(sentence_text)
                    valid_embeddings.append(embedding)
                else:
                    invalid_sentences.append(sentence_text)

        if not valid_embeddings:
            raise ValueError("No valid sentence embeddings found in the provided text.")

        valid_embeddings = cp.stack(valid_embeddings)
        similarities = self._compute_cosine_similarity(valid_embeddings)

        grouped_sentences = []
        group_idx = 0
        current_group = [valid_sentences[0]]
        pending_invalid_sentences = []

        for i in range(1, len(valid_sentences)):
            similarity = similarities[i, i - 1].item()

            if similarity >= self.similarity_threshold:
                current_group.append(valid_sentences[i])
            else:
                if pending_invalid_sentences:
                    grouped_sentences.append((" ".join(pending_invalid_sentences), -1))
                    pending_invalid_sentences.clear()

                grouped_sentences.append((" ".join(current_group), group_idx))
                group_idx += 1
                current_group = [valid_sentences[i]]

                if invalid_sentences:
                    pending_invalid_sentences.append(invalid_sentences.pop(0))

        if pending_invalid_sentences:
            grouped_sentences.append((" ".join(pending_invalid_sentences), -1))

        if current_group:
            grouped_sentences.append((" ".join(current_group), group_idx))

        return grouped_sentences


if __name__ == "__main__":
    test_text = """[youtube](https://www.youtube.com).\n\r HELLO!!"""

    grouper = SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.75)

    result = grouper.group_consecutive_similar_sentences(test_text)

    for sentence, group_index in result:
        print(f"Group {group_index}: {sentence}")