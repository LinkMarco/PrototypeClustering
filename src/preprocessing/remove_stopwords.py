from .preprocess import PreprocessBase
from nltk.corpus import stopwords

"""
Marco Link
"""

class CustomStopwords(PreprocessBase):
    """Class for removing stopwords"""

    def __init__(self, path_to_stop_list):
        """:param path_to_stop_list: the path to an existing text file which contains stopwords"""
        self._stop_list = stopwords.words(path_to_stop_list)

    def transform_string(self, text):
        word_list = text.split()
        new_word_list = []
        for word in word_list:
            if word.lower() not in self._stop_list:
                new_word_list.append(word)
        return " ".join(new_word_list)

    def transform_tokens(self, tokens):
        new_token_list = []
        for token in tokens:
            if token.lower() not in self._stop_list:
                new_token_list.append(token)
        return new_token_list


class EnglishStopwords(CustomStopwords):
    """Class for removing english stopwords."""

    def __init__(self):
        self._stop_list = stopwords.words('english')
