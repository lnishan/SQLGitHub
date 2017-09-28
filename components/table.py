"""A class to store tables."""


class SgTable:
    """A class to store tables."""

    def __init__(self):
        self._fields = []
        self._table = []

    def __len__(self):
        return len(self._table)

    def __iter__(self):
        for row in self._table:
            yield row

    def __getitem__(self, key):
        if not ((type(key) == int or type(key) == long) and key >= 0 and key < len(self._table)):
            raise ValueError("Index illegal")
        else:
            return self._table[key]

    def __setitem__(self, key, value):
        if not ((type(key) == int or type(key) == long) and key >= 0 and key < len(self._table)):
            raise ValueError("Index illegal")
        else:
            self._table[key] = value
    
    def Append(self, row):
        self._table.append(row)

    def GetTable(self):
        return self._table

    def SetTable(self, table):
        self._table = table

    def GetFields(self):
        return self._fields

    def SetFields(self, fields):
        self._fields = fields
