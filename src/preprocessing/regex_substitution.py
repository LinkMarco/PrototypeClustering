from .preprocess import PreprocessBase
import re

"""
Marco Link
"""

class RegexSubstitution(PreprocessBase):
    """Class for finding regular expressions and replace it with a specific _substitution"""

    def __init__(self, regex, substitution):
        """
        :param regex: the regular expression to search for
        :param substitution: the replacing string
        """
        self._regex = regex
        self._substitution = substitution

    def transform_string(self, text):
        # https://docs.python.org/3/library/re.html
        return re.sub(self._regex, self._substitution, text)

    def transform_tokens(self, tokens):
        return [re.sub(self._regex, self._substitution, token) for token in tokens]