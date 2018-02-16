import abc
from abc import ABCMeta
import csv
import numpy

"""
Marco Link
"""

class Reader(metaclass=ABCMeta):
    """Base Class for all reader objects."""

    def __init__(self, path, category_column, categories, text_field_columns):
        """
        :param path: the path to the input file
        :param category_column: the column which contains the categories
        :param categories: the actual categories
        :param text_field_columns: the column which contains the freeform texts
        """
        self._path = path
        self._category_column = category_column
        self._categories = categories
        self._text_fields_columns = text_field_columns

    @abc.abstractmethod
    def read(self):
        """Reads the specified file."""
        pass


class CSVReader(Reader):
    """A reader which can handle csv files."""
    def __init__(self, path, category_column, categories, text_field_columns, encoding='utf-8', delimiter='\t',
                 has_header=False):
        """
        :param path: the path to the input file
        :param category_column: the index of the column which contains the categories starting at 0
        :param categories: the actual categories
        :param text_field_columns: the indexes of the  columns which contains the freeform texts starting at 0
        :param encoding: the encoding from the csv file, default 'utf-8'
        :param delimiter: the delimiter of the csv file default tab character '\t'
        :param has_header: whether the csv file has a header with column names, default False
        """
        super().__init__(path, category_column, categories, text_field_columns)
        self._encoding = encoding
        self._delimiter = delimiter
        self._has_header = has_header

    def read(self):
        """
        Reads in the csv file.
        :return: Numpy array with the complete dataset and a numpy array with only the freeform text fields.
        """
        complete_dataset = []
        freeform_text_fields = []
        with open(self._path, encoding=self._encoding) as csv_file:
            j = 0
            csv_reader = csv.reader(csv_file, delimiter=self._delimiter)
            included_cols = [int(int(column)) for column in self._text_fields_columns]
            for row in csv_reader:
                # if a header is specified - just ignore it
                if self._has_header:
                    if j == 0:
                        j += 1
                        continue
                # check whether the category from the entry matches with the specified categories
                if row[int(self._category_column)] in self._categories:
                    complete_dataset.append(row)
                    freeform_text_fields.append(" ".join(row[i] for i in included_cols))
                j += 1
        return numpy.array(complete_dataset), numpy.array(freeform_text_fields)
