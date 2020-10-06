from similarity.helpers.number_helpers import is_number


class Tokenizer:
    SPLIT_CHARS = {' ', '\n', '\t', '\\'}
    PUNCTUATION_CHARS = {'.', ',', ';', ':', '"', "'", '?', '“', '”', '!', '-', '—', '—', '...', '\t', '(', ')', '[',
                         ']', '‘', '’', '+', '\n', '\\n', '*'}
    SPECIAL_CHARS_AS_TOKENS = {'@', '>', '<', '~', '%', '$', '£', '=', '/', '®', 'am', 'pm'} | PUNCTUATION_CHARS

    @staticmethod
    def build_token_dic(content, offset, label):
        return {
            'content': content,
            'offset': offset,
            'label': label
        }

    @staticmethod
    def next_char(text, cur_idx):
        if cur_idx + 1 >= len(text):
            return ''

        return text[cur_idx + 1]

    @staticmethod
    def pre_char(text, cur_idx):
        if cur_idx - 1 < 0:
            return ''

        return text[cur_idx - 1]

    def tokenize(self, text, index_to_label=None):
        if not index_to_label:
            index_to_label = {}

        token_list = []
        tmp_str = ''
        for idx, char in enumerate(text):
            tmp_str = tmp_str.strip(' ')
            if char in self.SPECIAL_CHARS_AS_TOKENS:
                if char in ['.', ','] and is_number(tmp_str) and is_number(self.next_char(text, idx)):
                    tmp_str += char

                elif char == '.' and self.next_char(text, idx).isalpha():
                    tmp_str += char

                else:
                    if tmp_str:
                        token_list.append(
                            self.build_token_dic(tmp_str, (idx - len(tmp_str), idx), index_to_label.get(idx - 1)))
                        tmp_str = ''

                    if char == '.' and self.next_char(text, idx).isalpha():
                        tmp_str += char
                    else:
                        token_list.append(self.build_token_dic(char, (idx, idx + 1), index_to_label.get(idx)))

            elif tmp_str in self.SPECIAL_CHARS_AS_TOKENS:
                if tmp_str == '.' and char.isalpha():
                    tmp_str += char
                else:
                    token_list.append(
                        self.build_token_dic(tmp_str, (idx - len(tmp_str), idx), index_to_label.get(idx - 1)))
                    tmp_str = char

            elif char in self.SPLIT_CHARS:
                if tmp_str:
                    token_list.append(
                        self.build_token_dic(tmp_str, (idx - len(tmp_str), idx), index_to_label.get(idx - 1)))
                    tmp_str = ''

                if char == '\\':
                    tmp_str = char

            else:
                tmp_str += char

        if tmp_str:
            text_len = len(text)
            token_list.append(
                self.build_token_dic(tmp_str, (text_len - len(tmp_str), text_len), index_to_label.get(text_len - 1)))

        return token_list
