import spacy
import cupy as cp

class SentenceGrouper:
    def __init__(self, model="nl_core_news_lg", similarity_threshold=0.75):
        self.nlp = spacy.load(model)
        spacy.prefer_gpu()
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def _cosine_similarity(x, y=None):
        if y is None:
            y = x

        x = cp.asarray(x)
        y = cp.asarray(y)

        dot_product = cp.dot(x, y.T)
        norm_x = cp.linalg.norm(x, axis=1, keepdims=True)
        norm_y = cp.linalg.norm(y, axis=1, keepdims=True)

        cosine_sim = dot_product / (norm_x * norm_y.T)
        return cosine_sim

    def group_consecutive_similar_sentences(self, text):
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
                    invalid_sentences.append(sentence_text)  # Track invalid sentences

        if not valid_embeddings:
            raise ValueError("No valid sentence embeddings found in the provided text.")

        valid_embeddings = cp.stack(valid_embeddings)
        similarities = self._cosine_similarity(valid_embeddings)

        labeled_sentences = []
        group_idx = 0
        current_group = [valid_sentences[0]]
        invalid_group = []  # Temporary list for invalid sentences

        for i in range(1, len(valid_sentences)):
            similarity = similarities[i, i - 1].item()

            if similarity >= self.similarity_threshold:
                current_group.append(valid_sentences[i])
            else:
                if invalid_sentences:  # There are invalid sentences between valid groups
                    # Handle invalid sentences as in-between group
                    if invalid_group:
                        # Add previous invalid group as a new group
                        labeled_sentences.append((" ".join(invalid_group), -1))
                        invalid_group = []  # Reset invalid group
                    # Add the current valid group
                    group_text = " ".join(current_group)
                    labeled_sentences.append((group_text, group_idx))
                    group_idx += 1
                else:
                    # Add the valid group without interspersed invalid sentences
                    group_text = " ".join(current_group)
                    labeled_sentences.append((group_text, group_idx))
                    group_idx += 1

                # Reset the current group and add the invalid sentences to an in-between group
                current_group = [valid_sentences[i]]

                # Add the invalid sentences as in-between group
                if invalid_sentences:
                    invalid_group.append(invalid_sentences.pop(0))

        # After the loop, check if there are any remaining invalid sentences to group
        if invalid_group:
            labeled_sentences.append((" ".join(invalid_group), -1))

        # Add the last valid group
        if current_group:
            group_text = " ".join(current_group)
            labeled_sentences.append((group_text, group_idx))

        return labeled_sentences


if __name__ == "__main__":
    test_text = """[youtube](https://www.youtube.com). jurreandenys@gmail.com. Ik ben cool. De appel is gay."""

    grouper = SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.75)

    result = grouper.group_consecutive_similar_sentences(test_text)

    for sentence, group_index in result:
        print(f"Group {group_index}: {sentence}")