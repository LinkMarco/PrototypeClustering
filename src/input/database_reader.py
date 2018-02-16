import pyodbc
import numpy

from .reader import Reader

"""
Marco Link
"""

class MSAccessDatabaseReader(Reader):
    """Class for reading database in MSAccess .mdb or .accdb format"""

    def __init__(self, path, category_column, categories, text_field_columns, table_name, username='admin',
                 password=''):
        """
        :param path: the path to the input file
        :param category_column: the column which contains the categories
        :param categories: the actual categories
        :param text_field_columns: the column which contains the freeform texts
        :param table_name: the table name to look for
        :param username: the username for the database default admin
        :param password: the password for the database default ''
        """
        super().__init__(path, category_column, categories, text_field_columns)
        self._table_name = table_name
        self._username = username
        self._password = password

    def read(self):
        """
        Reads in the ms access database.
        :return: Numpy array with the complete dataset and a numpy array with only the freeform text fields.
        """
        if self._text_fields_columns is None:
            return None

        if self._table_name is None:
            return None

        # Connection string for the database
        # http://stackoverflow.com/questions/1047580/ms-access-library-for-python
        odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % \
                        (self._path, self._username, self._password)

        # Establish connection to the database
        conn = pyodbc.connect(odbc_conn_str)

        # cursor which handles the sql statements
        cursor = conn.cursor()

        # whether more than one textfield was specified - crate a part of the SQL statement for getting the textfields
        if isinstance(self._text_fields_columns, list):
            text_fields_only = ', '.join(value for value in self._text_fields_columns)
        else:
            text_fields_only = self._text_fields_columns

        # Create the SQL statements for reading the database
        # One for the whole dataset and one for getting only the specified textfields
        only_text_fields_statement = "select " + text_fields_only + " from " + self._table_name
        complete_dataset_statement = "select * from " + self._table_name

        # nly getting the entries from the database according to the specified categories
        # whether there are multiple categories specified
        if isinstance(self._categories, list):
            only_text_fields_statement += " WHERE " + self._category_column + " IN (" \
                                          + ','.join("'" + category + "'" for category in self._categories) + ")"
            complete_dataset_statement += " WHERE " + self._category_column + " IN (" \
                                          + ','.join("'" + category + "'" for category in self._categories) + ")"
        # or only one category specified
        elif isinstance(self._categories, str):
            only_text_fields_statement += " WHERE " + self._category_column + " = '" + self._categories + "'"
            complete_dataset_statement += " WHERE " + self._category_column + " = '" + self._categories + "'"

        complete_dataset = []
        text_fields = []

        # fetch all text fields
        cursor.execute(only_text_fields_statement)
        row = cursor.fetchone()
        while row is not None:
            documents = []
            for document in row:
                if isinstance(document, str):
                    documents.append(document)
                else:
                    documents.append("")
            text_fields.append(" ".join(documents))

            row = cursor.fetchone()

        # fetch complete dataset
        cursor.execute(complete_dataset_statement)
        row = cursor.fetchone()
        while row is not None:
            complete_dataset.append(row)
            row = cursor.fetchone()

        # close database connection
        cursor.close()
        conn.close()

        return numpy.array(complete_dataset), numpy.array(text_fields)
