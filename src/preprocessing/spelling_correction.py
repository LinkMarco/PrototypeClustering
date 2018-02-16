from textblob import TextBlob
from .preprocess import PreprocessBase

"""
Marco Link
"""

class CorrectEnglishSpelling(PreprocessBase):
    """
    Class for applying english spelling correction with TextBlob
    https://textblob.readthedocs.io/en/dev/
    """
    # very slow for many documents!
    def transform_string(self, text):
        return TextBlob(text).correct()

    def transform_tokens(self, tokens):
        return [TextBlob(token).correct() for token in tokens]
