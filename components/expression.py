"""A set of utility functions to evaluate expressions.

Sample Usage:
    print(SgExpression.ExtractTokensFromExpression("name + issues_url"))
    print(SgExpression.ExtractTokensFromExpressions(["name + issues_url", "issues_url - id"]))
    print(SgExpression.EvaluateExpressionInRow(["a", "bb", "ccc"], [1, 2, 3], "bb + 2.0 + ccc / a"))
    print(SgExpression.EvaluateExpressionsInRow(["a", "bb", "ccc"], [1, 2, 3], ["bb + 2.0 + ccc / a", "a + bb + ccc"]))
    t = tb.SgTable()
    t.SetFields(["a", "bb", "ccc"])
    t.Append([1, 2, 3])
    t.Append([2, 4, 6])
    print(SgExpression.EvaluateExpressionsInTable(t, ["bb + 2.0 + ccc / a", "a + bb + ccc"]))
"""

import re

import table as tb


class SgExpression:
    """A set of utility functions to evaluate expressions."""

    # (?:something) means a non-capturing group
    # Matches anything word that isn't prefixed with a '"' (not a string literal) and postfixed with a '(' (not a function name)
    # Adding a non-alpha character as matching prefix/postfix to prevent cases like 'www(' having a match 'ww'
    _TOKEN_PRE = r"(?:[^\"\w_]|^)"
    _TOKEN_BODY = r"([\w_]+)"
    _TOKEN_POST = r"(?:[^\(\w_]|$)"
    _TOKEN_REGEX = _TOKEN_PRE + _TOKEN_BODY + _TOKEN_POST

    @staticmethod
    def ExtractTokensFromExpression(expr):
        return re.findall(SgExpression._TOKEN_REGEX, expr)

    @staticmethod
    def ExtractTokensFromExpressions(exprs):
        ret_set = set()
        for expr in exprs:
            for token in re.findall(SgExpression._TOKEN_REGEX, expr):
                ret_set.add(token)
        return list(ret_set)

    # TODO(lnishan): Add EvaluateExpressinInTable and make it a recursive function to correctly handle functions.
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
            expr = re.sub(re.compile(SgExpression._TOKEN_PRE + re.escape(pair[0]) + SgExpression._TOKEN_POST), val, expr)
        try:
            ret = eval(expr)
        except:
            ret = u""
            ret = expr
        return ret

    @staticmethod
    def EvaluateExpressionsInRow(fields, row, exprs):
        return [SgExpression.EvaluateExpressionInRow(fields, row, expr) for expr in exprs]

    @staticmethod
    def EvaluateExpressionsInTable(table, exprs):
        # TODO(lnishan): Support aggregating functions.
        #   Steps
        #     1. Detect and add additional fields (eg. MAX(<field name>)).
        #     2. Fill the values of the additional fields for each row.
        ret = tb.SgTable()
        ret.SetFields(exprs)
        for row in table:
            ret.Append(SgExpression.EvaluateExpressionsInRow(table.GetFields(), row, exprs))
        return ret
