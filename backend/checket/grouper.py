import spacy
import cupy as cp
from typing import List, Tuple
import re

import spacy
import cupy as cp
from typing import List, Tuple
import re

class SentenceGrouper:
    """
    A class for grouping consecutive, semantically similar sentences from text based on cosine similarity,
    with additional handling for open HTML tags.

    Parameters:
    - model (str): The SpaCy model to load for language processing (default: "nl_core_news_md").
    - similarity_threshold (float): The minimum cosine similarity score required for sentences to be grouped (default: 0.75).

    Methods:
    - group_consecutive_similar_sentences(text: str) -> List[Tuple[str, int]]:
        Groups consecutive sentences in the input text by semantic similarity. Each sentence group is returned
        as a tuple containing the grouped text and its associated group index. Sentences with open HTML tags
        are extended to include subsequent text up to the corresponding closing tag.
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

    @staticmethod
    def _find_open_html_tag(group: str) -> str:
        """Finds the open HTML tag in a given text group, if any."""
        match = re.search(r"<([a-zA-Z]+)[^>]*>", group)
        return match.group(1) if match else None

    @staticmethod
    def _has_closing_html_tag(group: str, tag: str) -> bool:
        """Checks if the group contains the closing tag for the given open HTML tag."""
        return bool(re.search(rf"</{tag}>", group))

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

        # Handle HTML tag grouping
        final_groups = []
        current_group_idx = 0
        skip_to_index = -1
        for i, (group_text, _) in enumerate(grouped_sentences):
            if i < skip_to_index:
                continue

            open_tag = self._find_open_html_tag(group_text)
            if open_tag:
                merged_text = group_text
                for j in range(i + 1, len(grouped_sentences)):
                    next_group, _ = grouped_sentences[j]
                    merged_text += " " + next_group
                    if self._has_closing_html_tag(next_group, open_tag):
                        skip_to_index = j + 1
                        break
                final_groups.append((merged_text, current_group_idx))
            else:
                final_groups.append((group_text, current_group_idx))

            current_group_idx += 1

        return final_groups

if __name__ == "__main__":
    test_text = """<strong>Welkom bij onze website!</strong> We bieden een breed scala aan informatie over verschillende onderwerpen. <a href="https://www.example.com">Visit Example Website!</a> De <i>appel</i> valt van de boom. De <i><strong>appel</strong></i> is groen!"""

    grouper = SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.80)

    result = grouper.group_consecutive_similar_sentences(test_text)

    for sentence, group_index in result:
        print(f"Group {group_index}: {sentence}")
