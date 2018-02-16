from nltk.tokenize import TreebankWordTokenizer, MWETokenizer, WhitespaceTokenizer
from nltk.corpus import stopwords


from preprocessing.preprocess import PreprocessBase

"""
Marco Link
"""

class Whitespace_Tokenizer(PreprocessBase):
    """ Class for using NLTKs Whitespace Tokenizer"""

    def __init__(self):
        self._tokenizer = WhitespaceTokenizer()

    def transform_string(self, text):
        return self._tokenizer.tokenize(text)

    def transform_tokens(self, tokens):
        new_tokens = []
        for old_token in tokens:
            for new_token in self._tokenizer.tokenize(old_token):
                new_tokens.append(new_token)
        return new_tokens


class PennTreebankWordTokenizer(PreprocessBase):
    """ Class for using NLTKs Treebank Word Tokenizer"""

    def __init__(self):
        self._tokenizer = TreebankWordTokenizer()

    def transform_string(self, text):
        return self._tokenizer.tokenize(text)

    def transform_tokens(self, tokens):
        new_tokens = []
        for old_token in tokens:
            for new_token in self._tokenizer.tokenize(old_token):
                new_tokens.append(new_token)
        return new_tokens


class MultiWordTokenizer(PreprocessBase):
    """Class for using NLTKs MWE Tokenizer for creating collocations."""

    def __init__(self, path_to_multi_words, separator=' '):
        """
        :param path_to_multi_words: the path to a list with specified collocations
        :param separator: how should the collocations be separated, default normal space character
        """
        multi_words_list = stopwords.words(path_to_multi_words)
        self._tokenizer = MWETokenizer(separator=separator)
        for multi_word in multi_words_list:
            multi_word = tuple(word for word in multi_word.split())
            self._tokenizer.add_mwe(multi_word)

    def transform_tokens(self, tokens):
        return self._tokenizer.tokenize(tokens)

    def transform_string(self, text):
        return " ".join(self._tokenizer.tokenize(text.split()))
