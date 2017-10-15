"""Functions for sorting tables."""

import random

from expression import SgExpression


class SgOrdering:

    def __init__(self, table, reverses):
        self._table = table
        self._reverses = reverses

    def _Swap(self, row1, row2):
        self._table[row1], self._table[row2] = self._table[row2], self._table[row1]

    def _Cmp(self, row1, row2):
        cmps = len(self._reverses)
        cmp1 = self._table[row1][-cmps:]
        cmp2 = self._table[row2][-cmps:]
        for i in range(cmps):
            if cmp1[i] < cmp2[i]:
                return -1 * self._reverses[i]
            elif cmp1[i] > cmp2[i]:
                return 1 * self._reverses[i]
        return 0

    def _Sort(self, low, high):
        if (low >= high):
            return
        pivot = low + random.randrange(high - low + 1)
        self._Swap(pivot, high)
        it = low
        for i in range(low, high):
            if self._Cmp(i, high) <= 0:
                self._Swap(it, i)
                it = it + 1
        self._Swap(it, high)
        self._Sort(low, it-1)
        self._Sort(it+1, high)

    def Sort(self, keep_order_fields=False):
        self._Sort(0, len(self._table)-1)
        return self._table.SliceCol(0, len(self._table.GetFields()) - len(self._reverses)) if not keep_order_fields else self._table


class SgTableOrdering:

    def __init__(self, tables, reverses):
        self._tables = tables
        self._reverses = reverses

    def _Swap(self, idx1, idx2):
        self._tables[idx1], self._tables[idx2] = self._tables[idx2], self._tables[idx1]

    def _Cmp(self, idx1, idx2):
        cmps = len(self._reverses)
        cmp1 = self._tables[idx1][0][-cmps:]
        cmp2 = self._tables[idx2][0][-cmps:]
        for i in range(cmps):
            if cmp1[i] < cmp2[i]:
                return -1 * self._reverses[i]
            elif cmp1[i] > cmp2[i]:
                return 1 * self._reverses[i]
        return 0

    def _Sort(self, low, high):
        if (low >= high):
            return
        pivot = low + random.randrange(high - low + 1)
        self._Swap(pivot, high)
        it = low
        for i in range(low, high):
            if self._Cmp(i, high) <= 0:
                self._Swap(it, i)
                it = it + 1
        self._Swap(it, high)
        self._Sort(low, it-1)
        self._Sort(it+1, high)

    def Sort(self):
        self._Sort(0, len(self._tables)-1)
        return [table.SliceCol(0, len(table.GetFields()) - len(self._reverses)) for table in self._tables]
