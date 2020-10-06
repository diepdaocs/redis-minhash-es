from similarity.nlp.preprocess.sentence_splitter import SentenceSplitter
from similarity.nlp.preprocess.tokenizer import Tokenizer


class PreprocessorIF:
    def process(self, texts, index_2_labels=None):
        raise NotImplementedError()


class SimplePreprocessor(PreprocessorIF):
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.sentence_splitter = SentenceSplitter()

    def process(self, texts, index_2_labels=None):
        if not index_2_labels:
            text_tokens_list = [self.tokenizer.tokenize(text) for text in texts]
        else:
            text_tokens_list = [self.tokenizer.tokenize(text, index_2_label) for text, index_2_label in
                                zip(texts, index_2_labels)]

        text_sentences = self.sentence_splitter.split_texts(text_tokens_list)

        return text_sentences
