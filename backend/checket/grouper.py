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

        for sent in doc.sents:
            sentence_text = sent.text.strip()
            if sentence_text:
                embedding = cp.array(sent.vector)
                if not cp.all(embedding == 0):
                    valid_sentences.append(sentence_text)
                    valid_embeddings.append(embedding)

        if not valid_embeddings:
            return [("No valid sentences with embeddings found.", 0)]

        valid_embeddings = cp.stack(valid_embeddings)

        similarities = self._cosine_similarity(valid_embeddings)

        labeled_sentences = []
        group_idx = 0
        current_group = [valid_sentences[0]]

        for i in range(1, len(valid_sentences)):
            similarity = similarities[i, i - 1].item()

            if similarity >= self.similarity_threshold:
                current_group.append(valid_sentences[i])
            else:
                if current_group:
                    labeled_sentences.extend(
                        [(sent, group_idx) for sent in current_group if sent]
                    )
                group_idx += 1
                current_group = [valid_sentences[i]]

        if current_group:
            labeled_sentences.extend(
                [(sent, group_idx) for sent in current_group if sent]
            )

        return labeled_sentences


if __name__ == "__main__":
    test_text = """
    Vanaf 28 september 2024 neemt Antwerpen de fakkel van het Ensorjaar over van Oostende met een veelzijdig en verrassend expoprogramma. Wat Antwerpen heeft met Ensor? Een gedeelde, verrassende blik voorbij het alledaagse. Die gaat al terug tot de tijd van Ensor zelf. Niet toevallig kwamen veel van zijn werken nog tijdens zijn leven in de Scheldestad terecht. Ze vormen vandaag de kern van de Ensor-collectie van het KMSKA en een vertrekpunt voor het Ensor Research Project. In zijn oeuvre laat Ensor zich - net als Antwerpen - kennen als een game-changer: vaak met een knipoog, soms dwars en altijd innovatief. Eigenschappen die Ensor tijdloos en relevant maken. Antwerpen kiest daarom voor verrassende invalshoeken om zijn werk te belichten. Hoe zien we echo’s van Ensor in de kunst, mode en fotografie? Hoe blijft hij inspireren en wat kunnen we vandaag nog van hem leren?
    """

    grouper = SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.75)

    result = grouper.group_consecutive_similar_sentences(test_text)

    for sentence, group_index in result:
        print(f"Group {group_index}: {sentence}")
