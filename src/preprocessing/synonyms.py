import csv

from preprocessing.preprocess import PreprocessBase

"""
Marco Link
"""

class SimpleSynonyms(PreprocessBase):
    """
    Class for replacing words with its specified synonyms.
    The synonyms has to be defined in a file.
    An entry in the file specifies the word which should be replaced followed by the tab character (\t) and its
    replacement.
    In the file one entry is separated with a newline character (\n).
    """

    def __init__(self, path):
        """:param path: the path to the synonyms file"""

        # read the synonyms file and hold it as a dictionary
        self._synonyms = {}
        # https://docs.python.org/3/library/csv.html
        with open(path, newline='') as synonyms_csv:
            synonyms_reader = csv.reader(synonyms_csv, delimiter='\t')
            for row in synonyms_reader:
                # if the row contains a word and its synonym to replace
                if len(row) > 1:
                    if row[0] not in self._synonyms:
                        self._synonyms.update({row[0]: row[1]})
                    else:
                        self._synonyms[row[0]] = row[1]

    def transform_string(self, text: str):
        return " ".join(self.transform_tokens(text.split()))

    def transform_tokens(self, tokens):
        new_tokens = []
        # for every token: search if it exists in the syonynm dictionary and replace it with its substitution
        for token in tokens:
            if token in self._synonyms:
                new_tokens.append(self._synonyms[token])
            else:
                new_tokens.append(token)
        return new_tokens


class ContextSynonyms(PreprocessBase):
    """
    Class for replacing a word with its specified synonym, if one of the specified context words is found
    in the surroundings.
    If found, both the main word to replace and the context word will be replaced with the specified substitution.
    It first searches before the main word for finding a context word and if not found after the main word.
    """

    def __init__(self, main_words, context_words, before, after, substitution):
        """
        :param main_words: the main words to search in their surroundings for context words
        :param context_words: the context words which should be searched in the surroundings from the main words
        :param before: how far before the main words should be searched
        :param after: how far after the main words should be searched
        :param substitution: the string to replace the found main word and context word
        """
        self._main_words = main_words
        self._context_words = context_words
        self._before = before
        self._after = after
        self._substitution = substitution

    def transform_string(self, text: str):
        return " ".join(self.transform_tokens(text.split()))

    def transform_tokens(self, tokens):
        new_tokens = tokens
        indizes_to_remove = []

        found_before = False
        found_after = False

        for index in range(len(new_tokens)):
            # was the token already removed with a previous context synonym?
            if index not in indizes_to_remove:

                token = new_tokens[index]
                # is the token one of the specified main words
                if token in self._main_words:
                    # search before the token for context words
                    # not enough words before existing as specified
                    if (index - self._before) <= 0:
                        words_before = new_tokens[0:index]
                        index_words_before = len(words_before) - 1
                        while index_words_before >= 0:
                            # was the token already removed with a previous context synonym?
                            if index_words_before not in indizes_to_remove:
                                if words_before[index_words_before] in self._context_words:
                                    found_before = True
                                    # for descendants context synonyms this word shouldn't be used and has to be
                                    # removed at the end
                                    indizes_to_remove.append(index_words_before)
                                    break
                            index_words_before -= 1
                    else:
                        words_before = new_tokens[index - self._before: index]
                        index_words_before = len(words_before) - 1
                        while index_words_before >= 0:
                            # was the token already removed with a previous context synonym?
                            if index_words_before not in indizes_to_remove:
                                if words_before[index_words_before] in self._context_words:
                                    found_before = True
                                    # for descendants context synonyms this word shouldn't be used and has to be
                                    # removed at the end
                                    indizes_to_remove.append(index - self._before + index_words_before)
                                    break
                            index_words_before -= 1

                    if not found_before:
                        if (index + self._after) > len(new_tokens):
                            if index < (len(new_tokens) - 1):
                                words_after = new_tokens[(index + 1): len(new_tokens)]
                                index_words_after = 0
                                while index_words_after < len(words_after):
                                    # was the token already removed with a previous context synonym?
                                    if index_words_after not in indizes_to_remove:
                                        if words_after[index_words_after] in self._context_words:
                                            found_after = True
                                            # for descendants context synonyms this word shouldn't be used and has
                                            # to be removed at the end
                                            indizes_to_remove.append(index + 1 + index_words_after)
                                            break
                                    index_words_after += 1
                        else:
                            words_after = new_tokens[index + 1: index + self._after]
                            index_words_after = 0
                            while index_words_after < len(words_after):
                                # was the token already removed with a previous context synonym?
                                if index_words_after not in indizes_to_remove:
                                    if words_after[index_words_after] in self._context_words:
                                        found_after = True
                                        # for descendants context synonyms this word shouldn't be used and has to be
                                        # removed at the end
                                        indizes_to_remove.append(index + 1 + index_words_after)
                                        break
                                index_words_after += 1

                    # replace the main word with the specified substitution
                    if found_before or found_after:
                        new_tokens[index] = self._substitution

        # return new tokens list, but without the found context words
        return [new_tokens[i] for i in range(len(new_tokens)) if i not in indizes_to_remove]
