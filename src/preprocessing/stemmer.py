from nltk import stem

from preprocessing.preprocess import PreprocessBase

"""
Marco Link
"""

class PorterStemmer(PreprocessBase):
    """Class for applying the Porter stemmer."""
    def __init__(self):
        self._stemmer = stem.PorterStemmer()

    def transform_string(self, text:str):
        return " ".join(self.transform_tokens(text.split()))

    def transform_tokens(self, tokens):
        return [self._stemmer.stem(token) for token in tokens]

class GermanStemmer(PreprocessBase):
    """Class for applying the german stemmer from nltk."""
    def __init__(self):
        self._stemmer = stem.snowball.GermanStemmer()

    def transform_string(self, text:str):
        return " ".join(self.transform_tokens(text.split()))

    def transform_tokens(self, tokens):
        return [self._stemmer.stem(token) for token in tokens]
