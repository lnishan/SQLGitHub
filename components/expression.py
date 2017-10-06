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

import definition as df
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

    @staticmethod
    def _IsFieldTokenCharacter(ch):
        return ch.isalpha() or ch == u"_"

    @staticmethod
    def _IsOperatorCharacter(ch):
        return not ch.isspace()

    @staticmethod
    def _IsNumericCharacter(ch):
        return ch.isdigit() or ch == u"."

    @staticmethod
    def _GetPrecedence(opr):
        return df.PRECEDENCE[opr] if opr else -100

    @staticmethod
    def _EvaluateOperatorBack(opds, oprs):
        opr = oprs[-1]
        oprs.pop()
        rows = len(opds)
        if opr == u",":  # special case: have to process every u","
            for i in range(rows):
                opds[i] = opds[i][:-2] + [opds[i][-2] + [opds[i][-1]]]
        elif opr == u"*":
            for i in range(rows):
                res = opds[i][-2] * opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"/":
            for i in range(rows):
                res = opds[i][-2] / opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"%":
            for i in range(rows):
                res = opds[i][-2] % opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"+":
            for i in range(rows):
                res = opds[i][-2] + opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"-":
            for i in range(rows):
                res = opds[i][-2] - opds[i][-1]
                opds[i] = opds[i][:-2] + [res]

    @staticmethod
    def _EvaluateFunction(opds, func):
        # print(opds, func)
        rows = len(opds)
        if func == "max":
            mx = max(row[-1] for row in opds)
            res = []
            for i in range(rows):
                res.append(mx)
            return res
        elif func == "min":
            mn = min(row[-1] for row in opds)
            res = []
            for i in range(rows):
                res.append(mn)
            return res
        else:
            res = [row[-1] for row in opds]
            return res

    @staticmethod
    def _EvaluateOperator(opds, oprs, opr=None):
        prec = SgExpression._GetPrecedence(opr)
        rows = len(opds)
        if opr == u"(":
            oprs.append(u"")
            oprs.append(opr)
        elif opr == u")":
            while oprs and oprs[-1] != u"(":
                SgExpression._EvaluateOperatorBack(opds, oprs)
            oprs.pop()
            func = oprs.pop().lower()
            if func:
                res = SgExpression._EvaluateFunction(opds, func)
                for i in range(rows):
                    opds[i][-1] = res[i]
        elif opr == u",":
            while oprs and SgExpression._GetPrecedence(oprs[-1]) >= prec and oprs[-1] != ",":
                SgExpression._EvaluateOperatorBack(opds, oprs)
            if (not oprs) or (oprs and oprs[-1] != ","):
                for i in range(rows):
                    opds[i][-1] = [opds[i][-1]]
            else:
                oprs.pop()
                for i in range(rows):
                    opds[i] = opds[i][:-2] + [opds[i][-2] + [opds[i][-1]]]
            oprs.append(opr)
        else:
            while oprs and SgExpression._GetPrecedence(oprs[-1]) >= prec :
                SgExpression._EvaluateOperatorBack(opds, oprs)
            if opr:
                oprs.append(opr)

    @staticmethod
    def _ProcessOperator(is_start, opds, oprs, token):
        rows = len(opds)
        token = token.lower()
        if token == u"-":
            token = u"--" if is_start else u"-"
        elif token == u"=":
            token = u"=="
        SgExpression._EvaluateOperator(opds, oprs, token)

    @staticmethod
    def EvaluateExpression(table, expr):
        rows = len(table)
        opds = []
        oprs = []
        for _ in range(rows):
            opds.append([])
        reading = None  # None = nothing, 0 = operator, 1 = field tokens (can be operator too), 2 = number, 3 = string
        is_start = True
        token = u""
        expr += u" "  # add a terminating character (to end token parsing)
        for ch in expr:
            if reading == 3:  # string
                token += ch
                if ch in (u"\"", u"\'"):
                    for i in range(rows):
                        opds[i].append(token)
                    token = u""
                    reading = None
            elif reading == 2:  # number
                if SgExpression._IsNumericCharacter(ch):
                    token += ch
                else:
                    num = float(token) if u"." in token else int(token)
                    for i in range(rows):
                        opds[i].append(num)
                    token = u""
                    if SgExpression._IsOperatorCharacter(ch):
                        reading = 0
                        token = ch
                    else:
                        reading = None
            elif reading == 1:
                if SgExpression._IsFieldTokenCharacter(ch):
                    token += ch
                else:
                    if token.lower() in df.OPERATOR_TOKENS:
                        SgExpression._ProcessOperator(is_start, opds, oprs, token)
                        token = u""
                        if ch.isspace():
                            reading = None
                        else:
                            token = ch
                            if ch in (u"\"", "\'"):
                                reading = 3
                            elif SgExpression._IsNumericCharacter(ch):
                                reading = 2
                            elif SgExpression._IsFieldTokenCharacter(ch):
                                reading = 1
                            elif SgExpression._IsOperatorCharacter(ch):
                                reading = 0
                    elif ch == u"(":  # function
                        oprs.append(token)
                        oprs.append(ch)
                        is_start = True
                        token = u""
                        reading = None
                    else:
                        vals = table.GetVals(token)
                        for i in range(rows):
                            opds[i].append(vals[i])
                        token = u""
                        if SgExpression._IsOperatorCharacter(ch):
                            reading = 0
                            token = ch
                        else:
                            reading = None
            elif reading == 0:
                if token == u"":
                    is_opr = True
                elif token == u")":
                    is_opr = False  # just to terminate the current segment
                elif ch == "(":
                    is_opr = False
                elif token.isalpha():
                    is_opr = ch.isalpha()
                else:
                    is_opr = (not ch.isalnum()) and (not ch.isspace())

                if is_opr:
                    token += ch
                else:
                    SgExpression._ProcessOperator(is_start, opds, oprs, token)
                    token = u""
                    if ch.isspace():
                        reading = None
                    else:
                        token = ch
                        if ch in (u"\"", "\'"):
                            reading = 3
                        elif SgExpression._IsNumericCharacter(ch):
                            reading = 2
                        elif SgExpression._IsFieldTokenCharacter(ch):
                            reading = 1
                        elif SgExpression._IsOperatorCharacter(ch):
                            reading = 0
            else:  # None
                if ch.isspace():
                    reading = None
                else:
                    token += ch
                    if ch in (u"\"", u"\'"):
                        reading = 3
                    elif SgExpression._IsNumericCharacter(ch) or (ch == u"-" and is_start):
                        reading = 2
                    elif SgExpression._IsFieldTokenCharacter(ch):
                        reading = 1
                    elif SgExpression._IsOperatorCharacter(ch):
                        reading = 0
                    is_start = False
            # print(opds, oprs)
        SgExpression._EvaluateOperator(opds, oprs)  # opr = None
        return [row[0] for row in opds]


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


if __name__ == "__main__":
    table = tb.SgTable()
    table.SetFields([u"a", u"b", u"a_b", u"c"])
    table.Append([1, 2, 3, u"A"])
    table.Append([2, 4, 6, u"BB"])
    table.Append([3, 6, 9, u"CCC"])
    print(SgExpression.EvaluateExpression(table, u"CONCAT(\"a\", c, \"ccc\")"))
    print(SgExpression.EvaluateExpression(table, u"MAX(a)"))
    print(SgExpression.EvaluateExpression(table, u"a LIKE \"ttt\""))
    print("---")
    print(SgExpression.EvaluateExpression(table, u"a * (b - a_b)"))
    print(SgExpression.EvaluateExpression(table, u"MIN(a * (b - a_b))"))
    print(SgExpression.EvaluateExpression(table, u"MAX(a * (b - a_b))"))
    print(SgExpression.EvaluateExpression(table, u"-7 + a*(b-a_b)"))
    print(SgExpression.EvaluateExpression(table, u"max(a*(b-a_b))"))
    print("---")
    print(SgExpression.EvaluateExpression(table, u"a * b - a_b + a_b % a"))
    print(SgExpression.EvaluateExpression(table, u"MIN(a * b - a_b + a_b % a)"))
    print(SgExpression.EvaluateExpression(table, u"MAX(a * b - a_b + a_b % a)"))
    print(SgExpression.EvaluateExpression(table, u"a*b-a_b+a_b%a"))
    print(SgExpression.EvaluateExpression(table, u"max(a*b-a_b+a_b%a)"))
