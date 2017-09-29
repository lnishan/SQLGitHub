"""A class to store conditions (eg. WHERE [cond])."""


class SgConditionSimple:
    """
    A class to store a simple condition.
    A simple condition is composed of 2 operands and 1 operator.
    """
    
    def __init__(self, operand-l, operator, operand-r):
        self._op-l = operand-l
        self._op = operator
        self._op-r = operand-r


class SgCondition:
    """A class to store a (complex) condition."""
    
    def __init__(self, expr):
        self._expr = expr
        self._conds = []  # simple conditions
        self._conns = []  # connectors (eg. and, or)
        # TODO(lnishan): parse expr into _conds and _conns.
    
    def Evaluate(self, fields, row):
        # TODO(lnishan): Evaluate the (complex) condition.
        return True
