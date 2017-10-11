"""A class to store tables.

Sample Usage:
    table = SgTable()
    table.Append([1, 2, 3])
    table.Append([2, 4, 6])
    table.Append([3, 6, 9])
    for row in table:
        print(row)
    print(table[1])
    table[1] = [2, 2, 2]
    print(table[1])
    table.SetFields(["a", "b", "c"])
    print(table.GetVals("a"))
    print(table.GetVals("b"))
    print(table.GetVals("c"))
    print(table[1:])
    print(table[:2])
    print(table[0:2:2])
"""


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
        if isinstance(key, slice):
            return self._table[key.start:key.stop:key.step]
        else:
            if not ((type(key) == int or type(key) == long) and key >= 0 and key < len(self._table)):
                raise ValueError("Index illegal")
            else:
                return self._table[key]

    def __setitem__(self, key, value):
        if not ((type(key) == int or type(key) == long) and key >= 0 and key < len(self._table)):
            raise ValueError("Index illegal")
        else:
            self._table[key] = value

    def __str__(self):
        ret = str(self._fields)
        for row in self._table:
            ret += "\n" + str(row)
        return ret

    def GetVals(self, field):
        idx = [i for i, f in enumerate(self._fields) if f == field][0]
        return [row[idx] for row in self._table]
    
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
    
    def SliceCol(self, start, end):
        table = SgTable()
        table.SetFields(self._fields[start:end])
        for row in self._table:
            table.Append(row[start:end])
        return table
