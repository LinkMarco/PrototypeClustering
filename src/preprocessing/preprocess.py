import abc
from abc import ABCMeta
import numpy

"""
Marco Link
"""

class PreprocessBase(metaclass=ABCMeta):
    """
    The preprocess base class, all preprocessing classes should be inherit from it.
    """

    def transform(self, documents):
        """
        Transforms given documents.
        :param documents: the documents to transform, a document can be a string or a collection of tokens
        :return: the transformed documents
        """

        new_documents = []
        for document in documents:
            # transform string, if the document is a string
            if isinstance(document, str):
                transformed_text = self.transform_string(document)
                new_documents.append(transformed_text)

            # or transform tokens, if the document contains of a list with tokens
            else:
                transformed_tokens = self.transform_tokens(document)
                new_documents.append(transformed_tokens)

        return numpy.array(new_documents)

    @abc.abstractmethod
    def transform_string(self, text):
        """
        Transforms a string.
        :param text: the text to transform
        :return: the transformed text
        """
        ...

    @abc.abstractmethod
    def transform_tokens(self, tokens):
        """
        Transforms a collection of tokens.
        :param tokens: the tokens to transform
        :return: the transformed tokens
        """
        ...


class ToLowercase(PreprocessBase):
    """
    Preprocess class to transform a string or tokens to lowercase.
    """
    def transform_string(self, text):
        """
        Transforms a string to lowercase.
        :param text: the string to transform
        :return: the transformed string
        """
        return text.lower()

    def transform_tokens(self, tokens):
        """
        Transform a list of tokens to lowercase.
        :param tokens: the list of tokens to transform
        :return: a list with the transformed tokens.
        """
        return [token.lower() for token in tokens]
