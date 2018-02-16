"""
This module contains useful preprocessing steps from the library Textacy
https://github.com/chartbeat-labs/textacy

For fruther informations to the preprocessing methods see:
https://github.com/chartbeat-labs/textacy/blob/master/textacy/preprocess.py
"""
from textacy import preprocess

from .preprocess import PreprocessBase


class UnpackContractions(PreprocessBase):
    """Transforms english contractions to its full form. Example: didn't -> did not"""
    def transform_string(self, text):
        return preprocess.unpack_contractions(text)

    def transform_tokens(self, tokens):
        return [preprocess.unpack_contractions(token) for token in tokens]


class NormalizeWhitespace(PreprocessBase):
    """If there are more than one space between words, they will be replaced with one."""
    def transform_string(self, text):
        return preprocess.normalize_whitespace(text)

    def transform_tokens(self, tokens):
        return [preprocess.normalize_whitespace(token) for token in tokens]


class ReplaceUrls(PreprocessBase):
    """Replaces urls with the specified _substitution"""
    def __init__(self, replace_with=''):
        """:param replace_with: the _substitution"""
        self._replace_with = replace_with

    def transform_string(self, text):
        return preprocess.replace_urls(text, replace_with=self._replace_with)

    def transform_tokens(self, tokens):
        return [preprocess.replace_urls(token, replace_with=self._replace_with) for token in tokens]


class ReplaceEMails(PreprocessBase):
    """Replaces email adresses with the specified _substitution"""
    def __init__(self, replace_with=''):
        """:param replace_with: the _substitution"""
        self._replace_with = replace_with

    def transform_string(self, text):
        return preprocess.replace_emails(text, replace_with=self._replace_with)

    def transform_tokens(self, tokens):
        return [preprocess.replace_emails(token, replace_with=self._replace_with) for token in tokens]


class ReplacePhoneNumbers(PreprocessBase):
    """Replaces phone numbers with the specified _substitution"""
    def __init__(self, replace_with=''):
        """:param replace_with: the _substitution"""
        self._replace_with = replace_with

    def transform_string(self, text):
        return preprocess.replace_phone_numbers(text, replace_with=self._replace_with)

    def transform_tokens(self, tokens):
        return [preprocess.replace_phone_numbers(token, replace_with=self._replace_with) for token in tokens]


class ReplaceNumbers(PreprocessBase):
    """Replaces numbers with the specified _substitution"""
    def __init__(self, replace_with=''):
        """:param replace_with: the _substitution"""
        self._replace_with = replace_with

    def transform_string(self, text):
        return preprocess.replace_numbers(text, replace_with=self._replace_with)

    def transform_tokens(self, tokens):
        return [preprocess.replace_numbers(token, replace_with=self._replace_with) for token in tokens]


class RemovePunct(PreprocessBase):
    """Replaces the punctuation symbols with empty strings."""
    def transform_string(self, text):
        return preprocess.remove_punct(text)

    def transform_tokens(self, tokens):
        transformed_tokens = []
        for token in tokens:
            token = preprocess.remove_punct(token)
            if token != '':
                transformed_tokens.append(token)
        return transformed_tokens


class ReplaceCurrencySymbols(PreprocessBase):
    """Replaces currency symbols with the specified _substitution"""
    def __init__(self, replace_with=None):
        """:param replace_with: the _substitution"""
        self._replace_with = replace_with

    def transform_string(self, text):
        return preprocess.replace_currency_symbols(text, replace_with=self._replace_with)

    def transform_tokens(self, tokens):
        return [preprocess.replace_currency_symbols(token, replace_with=self._replace_with) for token in tokens]


class RemoveAccents(PreprocessBase):
    def __init__(self, method='unicode'):
        self._method = method

    def transform_string(self, text):
        return preprocess.remove_accents(text, self._method)

    def transform_tokens(self, tokens):
        return [preprocess.remove_accents(token, self._method) for token in tokens]


class FixBadUnicode(PreprocessBase):
    def __init__(self, normalization='NFC'):
        self._normalization = normalization

    def transform_string(self, text):
        return preprocess.fix_bad_unicode(text, self._normalization)

    def transform_tokens(self, tokens):
        return [preprocess.fix_bad_unicode(token, self._normalization) for token in tokens]
