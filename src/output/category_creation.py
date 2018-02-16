from abc import ABCMeta, abstractmethod
import pyodbc

"""
Marco Link
"""

class CategoryCreator(metaclass=ABCMeta):
    """Base Class for classes which will create categories for a specific dataset."""
    def __init__(self, path):
        self._path = path

    @abstractmethod
    def create_categories(self):
        pass


class NHTSADatabaseCategoryCreation(CategoryCreator):
    """Class for creating categories for the nhtsa consumer complaint's database from its component description."""
    def __init__(self, path, table_name='FLAT_CMPL', username='admin', password='', primary_key_column='Feld1',
                 category_column='Category'):
        """
        :param path: the path to the database
        :param table_name: the table name to look for
        :param username: the username for the database default admin
        :param password: the password for the database default ''
        :param category_column: the name of the new field
        :param primary_key_column: the field which contains the primary key
        """
        super().__init__(path)
        self._table_name = table_name
        self._username = username
        self._password = password
        self._category_column = category_column
        self._primary_key_column = primary_key_column

    def create_categories(self):
        """Creates new field in the database and gives every entry from the dataset a category."""

        # http://stackoverflow.com/questions/1047580/ms-access-library-for-python
        odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % \
                        (self._path, self._username, self._password)

        conn = pyodbc.connect(odbc_conn_str)
        cursor = conn.cursor()

        # https://msdn.microsoft.com/en-us/library/office/bb177883(v=office.12).aspx
        cursor.execute(' '.join(['alter table', self._table_name, 'add column', self._category_column, 'varchar(128)']))
        conn.commit()

        cursor.execute(' '.join(['select * from', self._table_name]))

        # create update statements for the database
        updatestmnts = []
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            key = row[0]
            compdesc = row[11]
            category = self.get_category(compdesc)
            if category is None:
                continue
            updatestmnt = 'UPDATE ' + self._table_name + ' SET ' + self._category_column + ' = ' \
                          + "'" + category + "'" + ' WHERE ' + self._primary_key_column + ' = ' + str(key)
            updatestmnts.append(updatestmnt)

        # update the database
        for updatestmnt in updatestmnts:
            cursor.execute(updatestmnt)
            conn.commit()

        cursor.close()
        conn.close()

    def get_category(self, compdesc):
        """
        Returns the actual category after some categories from the nhtsa dataset were merged.
        :param compdesc: the original root component of the component description
        :return: str
        """
        if isinstance(compdesc, str):
            a = compdesc.split(":")
            category = a[0]

            if category == 'CHILD SEAT':
                category = 'SEATS'
            elif category == 'SEAT BELTS':
                category = 'SEATS'

            elif category == 'FUEL/PROPULSION SYSTEM':
                category = 'PROPULSION SYSTEM'
            elif category == 'HYBRID PROPULSION SYSTEM':
                category = 'PROPULSION SYSTEM'
            elif category == 'FUEL SYSTEM, GASOLINE':
                category = 'PROPULSION SYSTEM'
            elif category == 'FI':
                category = 'PROPULSION SYSTEM'
            elif category == 'FUEL SYSTEM, DIESEL':
                category = 'PROPULSION SYSTEM'
            elif category == 'FUEL SYSTEM, OTHER':
                category = 'PROPULSION SYSTEM'

            elif category == 'OTHER':
                category = 'UNKNOWN OR OTHER'
            elif category == '':
                category = 'UNKNOWN OR OTHER'

            elif category == 'SERVICE BRAKES, HYDRAULIC':
                category = 'BRAKES'
            elif category == 'SERVICE BRAKES, ELECTRIC':
                category = 'BRAKES'
            elif category == 'SERVICE BRAKES, AIR':
                category = 'BRAKES'
            elif category == 'PARKING BRAKE':
                category = 'BRAKES'
            elif category == 'SERVICE BRAKES':
                category = 'BRAKES'

            elif category == 'EQUIPMENT ADAPTIVE':
                category = 'EQUIPMENT'

            elif category == 'ENGINE':
                category = 'ENGINE AND ENGINE COOLING'

            elif category == 'WHEELS':
                category = 'TIRES'

            elif category == 'AIR BAG':
                category = 'AIR BAGS'

            elif category == 'TRAILER HITCHES':
                category = 'TRAILER HARDWARE'

            elif category == 'BACK OVER PREVENTION':
                category = 'ELECTRICAL SYSTEM'
            elif category == 'FORWARD COLLISION AVOIDANCE':
                category = 'ELECTRICAL SYSTEM'
            elif category == 'TRACTION CONTROL SYSTEM':
                category = 'ELECTRICAL SYSTEM'
            elif category == 'LANE DEPARTURE':
                category = 'ELECTRICAL SYSTEM'

            elif category == 'EXTERIOR LIGHTING':
                category = 'LIGHTING'
            elif category == 'INTERIOR LIGHTING':
                category = 'LIGHTING'

            elif category == 'LATCHES/LOCKS/LINKAGES':
                category = 'STRUCTURE'

            elif category == 'VISIBILITY/WIPER':
                category = 'VISIBILITY'

            return category

        return 'UNKNOWN OR OTHER'
