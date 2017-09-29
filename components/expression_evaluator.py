"""A set of utility functions to evaluate expressions.

Sample Usage:
    print(SgExpressionEvaluator.EvaluateExpressionInRow(["a", "bb", "ccc"], [1, 2, 3], "bb + 2.0 + ccc / a"))
    print(SgExpressionEvaluator.EvaluateExpressionsInRow(["a", "bb", "ccc"], [1, 2, 3], ["bb + 2.0 + ccc / a", "a + bb + ccc"]))
    t = tb.SgTable()
    t.SetFields(["a", "bb", "ccc"])
    t.Append([1, 2, 3])
    t.Append([2, 4, 6])
    print(SgExpressionEvaluator.EvaluateExpressionsInTable(t, ["bb + 2.0 + ccc / a", "a + bb + ccc"]))
"""

import table as tb


class SgExpressionEvaluator:
    """A set of utility functions to evaluate expressions."""

    @staticmethod
    def EvaluateExpressionInRow(fields, row, expr):
        """
        Evaluates the results of an expression (presumably a non-terminal field)
        given a list of fields and the values of a row.
        """

        # TODO(lnishan): This works for now, but in the future we might want to implement
        # a proper evaluator (correct tokenization, 2-stack evaluation)
        pairs = zip(fields, row)
        pairs.sort(key=lambda p: len(p[0]), reverse=True)
        for pair in pairs:
            val = pair[1] if isinstance(pair[1], unicode) else unicode(str(pair[1]), "utf-8")
            expr = expr.replace(pair[0], val)
        try:
            ret = eval(expr)
        except:
            ret = u""
            ret = expr
        return ret

    @staticmethod
    def EvaluateExpressionsInRow(fields, row, exprs):
        return [SgExpressionEvaluator.EvaluateExpressionInRow(fields, row, expr) for expr in exprs]

    @staticmethod
    def EvaluateExpressionsInTable(table, exprs):
        # TODO(lnishan): Support aggregating functions.
        #   Steps
        #     1. Detect and add additional fields (eg. MAX(<field name>)).
        #     2. Fill the values of the additional fields for each row.
        ret = tb.SgTable()
        ret.SetFields(exprs)
        for row in table:
            ret.Append(SgExpressionEvaluator.EvaluateExpressionsInRow(table.GetFields(), row, exprs))
        return ret
