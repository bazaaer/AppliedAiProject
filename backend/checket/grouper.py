import spacy
import cupy as cp
import html2text
import markdown2
import re
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
        self.html2text = html2text.HTML2Text()
        self.markdown = markdown2.Markdown()

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

    def _html_to_markdown_to_html(self, html_text: str) -> str:
        markdown_text = self.html2text.handle(html_text)
        return self.markdown.convert(markdown_text)

    def _is_markdown_sentence(self, sentence: str) -> bool:
        """
        Check if the sentence contains Markdown formatting (e.g., **bold**, *italic*, etc.).
        """
        markdown_patterns = [r'\*\*.*\*\*', r'\*.*\*', r'~~.*~~', r'__.*__', r'``.*``']
        return any(re.search(pattern, sentence) for pattern in markdown_patterns)

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

            # If the current sentence or the previous sentence contains Markdown formatting, treat it as a single group
            if self._is_markdown_sentence(valid_sentences[i]) or self._is_markdown_sentence(valid_sentences[i - 1]):
                current_group.append(valid_sentences[i])
            elif similarity >= self.similarity_threshold:
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

        # Now, convert each sentence group from HTML to Markdown and back to HTML
        final_grouped_sentences = []
        for sentence_group, group_idx in grouped_sentences:
            html_sentence_group = f"<p>{sentence_group}</p>"
            html_to_html = self._html_to_markdown_to_html(html_sentence_group)
            final_grouped_sentences.append((html_to_html, group_idx))

        return final_grouped_sentences


if __name__ == "__main__":
    test_text = """<p><strong>Welkom bij onze website!</strong> We bieden een breed scala aan informatie over verschillende onderwerpen. <a href="https://www.example.com">Visit Example Website!</a> De <i>appel</i> valt van de boom. De appel is groen!</p>"""

    grouper = SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.50)

    result = grouper.group_consecutive_similar_sentences(test_text)

    for sentence, group_index in result:
        print(f"Group {group_index}: {sentence}")
