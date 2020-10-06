class SentenceSplitter:
    SPLIT_SENTENCE_CHARS = {'\n', '\\n', '.'}

    def split(self, tokens):
        result = []
        tmp_sen = []
        for token in tokens:
            word = token['content']
            if word in self.SPLIT_SENTENCE_CHARS:
                if tmp_sen:
                    result.append(tmp_sen)
                    tmp_sen = []
            else:
                tmp_sen.append(token)

        if tmp_sen:
            result.append(tmp_sen)

        return result

    def split_texts(self, text_tokens_list):
        text_sents = []
        for text_tokens in text_tokens_list:
            text_sents.append(self.split(text_tokens))

        return text_sents
