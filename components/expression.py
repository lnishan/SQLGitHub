"""A set of utility functions to evaluate expressions.

Sample Usage:
    print(SgExpression.ExtractTokensFromExpression("name + issues_url"))
    print(SgExpression.ExtractTokensFromExpressions(["name + issues_url", "issues_url - id"]))
    print(SgExpression.IsAllTokensInAggregate(["avg(mycount + 5)", "max(5 + min(yo))"]))
    print(SgExpression.IsAllTokensInAggregate(["avg(mycount + 5) + secondcount", "max(5 + min(yo))"]))
    table = tb.SgTable()
    table.SetFields([u"a", u"b", u"a_b", u"c"])
    table.Append([1, 2, 3, u"A"])
    table.Append([2, 4, 6, u"BB"])
    table.Append([3, 6, 9, u"CCC"])
    table.Append([4, 8, 12, u"ABC"])
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
    print("---")
    print(SgExpression.EvaluateExpression(table, u"3 + 2 = 5"))
    print(SgExpression.EvaluateExpression(table, u"6 = 3 + 2"))
    print(SgExpression.EvaluateExpression(table, u"a_b * a_b - b > 10"))
    print(SgExpression.EvaluateExpression(table, u"\"aaa\" is \"aaa\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"%\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"%A\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"C_C\""))
    print(SgExpression.EvaluateExpression(table, u"c like \"A\""))
    print(SgExpression.EvaluateExpression(table, "\"%%%\" like \"\\%_\\%\""))
    print(SgExpression.EvaluateExpression(table, "\"a%%\" like \"\\%_\\%\""))
    print(SgExpression.EvaluateExpression(table, "\"%a%\" like \"\\%_\\%\""))
    print(SgExpression.EvaluateExpression(table, u"c regexp \"B*\""))
    print(SgExpression.EvaluateExpression(table, u"c regexp \"[B-C]*\""))
    print(SgExpression.EvaluateExpression(table, u"\"BB\" in (\"A\", \"B\", c)"))
    print("---")
    print(SgExpression.EvaluateExpression(table, "not a + 2 >= b"))
    print(SgExpression.EvaluateExpression(table, "not a + 2 >= b and a_b > 10"))
    print(SgExpression.EvaluateExpression(table, "b < 5 || a_b > 10"))
    print("---")
    print(SgExpression.EvaluateExpression(table, "sum(a + b)"))
    print(SgExpression.EvaluateExpression(table, "avg(a * a)"))
    print(SgExpression.EvaluateExpression(table, u"CONCAT(\"a\", c, \"ccc\", -7 + 8)"))
"""

import re
import regex  # need recursive pattern

import definition as df
import utilities as util
import table as tb
import math
from datetime import date

class SgExpression:
    """A set of utility functions to evaluate expressions."""

    # (?:something) means a non-capturing group
    # Matches anything word that isn't postfixed with a '(' (not a function name)
    # Adding a non-alpha character as matching postfix to prevent cases like 'www(' having a match 'ww'
    _TOKEN_BODY = r"([a-zA-Z_]+)"
    _TOKEN_POST = r"(?:[^\(a-zA-Z_]|$)"
    _TOKEN_REGEX = _TOKEN_BODY + _TOKEN_POST
    _DBL_STR_REGEX = r"\"(?:[^\\\"]|\\.)*\""
    _SGL_STR_REGEX = r"\'(?:[^\\\']|\\.)*\'"

    @classmethod
    def ExtractTokensFromExpressions(cls, exprs):
        ret_set = set()
        for expr in exprs:
            if expr == u"*":
                return [u"*"]
            expr_rem = re.sub(cls._DBL_STR_REGEX, r"", expr)
            expr_rem = re.sub(cls._SGL_STR_REGEX, r"", expr_rem)  # string literals removed
            for token in re.findall(cls._TOKEN_REGEX, expr_rem):
                if not token in df.ALL_TOKENS:
                    ret_set.add(token)
        return list(ret_set)

    @classmethod
    def IsAllTokensInAggregate(cls, exprs):
        aggr_regex = r"((?:" + r"|".join(df.AGGREGATE_FUNCTIONS) + r")\((?:(?>[^\(\)]+|(?R))*)\))"
        for expr in exprs:
            expr_rem = re.sub(cls._DBL_STR_REGEX, r"", expr)
            expr_rem = re.sub(cls._SGL_STR_REGEX, r"", expr_rem)  # string literals removed
            while True:
                prev_len = len(expr_rem)
                expr_rem = regex.sub(aggr_regex, r"", expr_rem)  # one aggregate function removed
                if len(expr_rem) == prev_len:
                    break
            if re.search(cls._TOKEN_REGEX, expr_rem):
                return False
        return True

    @classmethod
    def _IsFieldTokenCharacter(cls, ch):
        return ch.isalpha() or ch == u"_"

    @classmethod
    def _IsOperatorCharacter(cls, ch):
        return not ch.isspace()

    @classmethod
    def _IsNumericCharacter(cls, ch):
        return ch.isdigit() or ch == u"."

    @classmethod
    def _GetPrecedence(cls, opr):
        return df.PRECEDENCE[opr] if opr else -100

    @classmethod
    def _EvaluateOperatorBack(cls, opds, oprs):
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
        elif opr == u"==":  # shouldn't work with None but it does atm
            for i in range(rows):
                res = opds[i][-2] == opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u">=":
            for i in range(rows):
                res = opds[i][-2] >= opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u">":
            for i in range(rows):
                res = opds[i][-2] > opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"<=":
            for i in range(rows):
                res = opds[i][-2] <= opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"<":
            for i in range(rows):
                res = opds[i][-2] < opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"<>":
            for i in range(rows):
                res = opds[i][-2] != opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"!=":
            for i in range(rows):
                res = opds[i][-2] != opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"is":
            for i in range(rows):
                res = opds[i][-2] == opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"like":
            for i in range(rows):
                is_escaping = False
                regex = r""
                for ch in opds[i][-1]:
                    if is_escaping:  # \% \_
                        regex += ch
                        is_escaping = False
                    elif ch == "\\":
                        is_escaping = True
                    elif ch == "%":
                        regex += ".*"
                    elif ch == "_":
                        regex += "."
                    else:
                        regex += re.escape(ch)
                regex += r"$"
                res = True if opds[i][-2] and re.match(regex, opds[i][-2]) else False
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"regexp":
            for i in range(rows):
                regex = re.compile(opds[i][-1] + "$")
                res = True if opds[i][-2] and re.match(regex, opds[i][-2]) else False
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"in":
            for i in range(rows):
                res = opds[i][-2] in opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == u"not":
            for i in range(rows):
                opds[i][-1] = not opds[i][-1]
        elif opr in (u"and", u"&&"):
            for i in range(rows):
                res = opds[i][-2] and opds[i][-1]
                opds[i] = opds[i][:-2] + [res]
        elif opr == "xor":
            for i in range(rows):
                res = opds[i][-2] != opds[i][-1]  # assumes both are boolean's
                opds[i] = opds[i][:-2] + [res]
        elif opr in (u"or", u"||"):
            for i in range(rows):
                res = opds[i][-2] or opds[i][-1]
                opds[i] = opds[i][:-2] + [res]

    @classmethod
    def _EvaluateFunction(cls, opds, func):
        # TODO(lnishan): Add new function names to definitions.py
        rows = len(opds)
        if func == "zero":  # dummy function
            return [0] * rows
        if func == "avg":
            avg = sum(row[-1] for row in opds) / float(rows)
            res = []
            for i in range(rows):
                res.append(avg)
            return res
        elif func == "count":
            res = []
            for i in range(rows):
                res.append(rows)
            return res
        elif func == "max":
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
        elif func == "sum":
            sm = sum(row[-1] for row in opds)
            res = []
            for i in range(rows):
                res.append(sm)
            return res
        elif func == "ascii":
            res = []
            for row in opds:
                res.append(u" ".join(str(ord(i)) for i in row[-1]))
            return res
        elif func == "concat":
            res = []
            for row in opds:
                cstr = u""
                for val in row[-1]:
                    cstr += util.GuaranteeUnicode(val)
                res.append(cstr)
            return res
        elif func == "concat_ws":
            res = []
            for row in opds:
                cstr = u""
                sep = row[-1][0]
                for val in row[-1][:-1]:
                    if val != sep:
                        cstr += util.GuaranteeUnicode(val)
                        cstr += sep
                cstr += util.GuaranteeUnicode(row[-1][-1])
                res.append(cstr)
            return res
        elif func == "find_in_set":
            res =[]
            for row in opds:
                cstr = row[-1][-1]
                subs = row[-1][-2]
                if subs in cstr:
                    res.append(cstr.index(subs)+1)
                else:
                    res.append(0)
            return res
        elif func == "insert":
            res = []
            for row in opds:
                x = row[-1][-3] - 1
                y = row[-1][-2]
                str = row[-1][-4]
                subs = row[-1][-1]
                res.append(str[:x] + subs + str[x+y-1:])
            return res
        elif func == "instr":
            res = []
            for row in opds:
                res.append(row[-1][-2].find(row[-1][-1])+1)
            return res
        elif func in (u"lcase", u"lower"):
            res = []
            for row in opds:
	        res.append(row[-1].lower())
            return res
        elif func == "left":
            res = []
            for row in opds:
                n_char = row[-1][-1]
                subs = row[-1][-2]
                res.append(subs[:n_char])
            return res
        elif func == "length":
            res = []
            for row in opds:
                res.append(len(row[-1]))
            return res
        elif func == "locate":
            res = []
            for row in opds:
                x = len(row[-1])
                if x == 3:
                    st_pos = row[-1].pop()
                cstr = row[-1].pop()
                subs = row[-1].pop()
                if x == 3:
                    res.append(cstr.find(subs, st_pos)+1)
                else:
                    res.append(cstr.find(subs)+1)
            return res
        elif func in (u"mid", u"substr", u"substring"):
            res = []
            for row in opds:
                x = len(row[-1])
                if x == 3:
                    n_len = row[-1].pop()
                n_st = row[-1].pop() - 1
                subs = row[-1].pop()
                if x == 3:
                    n_end = n_st + n_len
                    res.append(subs[n_st:n_end]) 
                else:
                    res.append(subs[n_st:])
            return res 
        elif func == "repeat":
            res = []
            for row in opds:
                cstr = u""
                for i in range(row[-1][-1]):
                    cstr += row[-1][-2]
                res.append(cstr)
            return res
        elif func == "replace":
            res = []
            for row in opds:
                res.append(row[-1][-3].replace(row[-1][-2],row[-1][-1]))
            return res  
        elif func == "right":
            res = []
            for row in opds:
                n_char = row[-1][-1]
                subs = row[-1][-2]
                res.append(subs[-n_char:])
            return res
        elif func == "strcmp":
            res = []
            for row in opds:
                res.append((row[-1][-1] == row[-1][-2]))
            return res
        elif func in (u"ucase", u"upper"):
            res = []
            for row in opds:
                res.append(row[-1].upper())
            return res
        elif func == "abs":
            res = []
            for row in opds:
                res.append(abs(row[-1]))
            return res
        elif func in (u"ceil", u"ceiling"):
            res = []
            for row in opds:
                res.append(math.ceil(row[-1]))
            return res
        elif func == "exp":
            res = []
            for row in opds:
                res.append(math.exp(row[-1]))
                return res
        elif func == "floor":
            res = []
            for row in opds:
                res.append(math.floor(row[-1]))
                return res
        elif func == "greatest":
            res = []
            for row in opds:
                res.append(max(row[-1]))
            return res
        elif func == "least":
            res = []
            for row in opds:
                res.append(min(row[-1]))
            return res  
        elif func in (u"ln", u"log"):
            res = []
            for row in opds:
                res.append(math.log(row[-1]))
            return res
        elif func in (u"pow", u"power"):
            res = []
            for row in opds:
                res.append(math.pow(row[-1][-2], row[-1][-1]))
            return res
        elif func == "sign":
            res = []
            for row in opds:
                res.append((row[-1] > 0) - (row[-1] < 0))
            return res
        elif func == "sqrt":
            res = []
            for row in opds:
                res.append(math.sqrt(row[-1]))
            return res
        else:
            res = [row[-1] for row in opds]
            return res

    @classmethod
    def _EvaluateOperator(cls, opds, oprs, opr=None):
        prec = cls._GetPrecedence(opr)
        rows = len(opds)
        if opr == u"(":
            oprs.append(u"")
            oprs.append(opr)
        elif opr == u")":
            while oprs and oprs[-1] != u"(":
                cls._EvaluateOperatorBack(opds, oprs)
            oprs.pop()
            func = oprs.pop().lower()
            if func:
                res = cls._EvaluateFunction(opds, func)
                for i in range(rows):
                    opds[i][-1] = res[i]
        elif opr == u",":
            while oprs and cls._GetPrecedence(oprs[-1]) >= prec and oprs[-1] != ",":
                cls._EvaluateOperatorBack(opds, oprs)
            if (not oprs) or (oprs and oprs[-1] != ","):
                for i in range(rows):
                    opds[i][-1] = [opds[i][-1]]
            else:
                oprs.pop()
                for i in range(rows):
                    opds[i] = opds[i][:-2] + [opds[i][-2] + [opds[i][-1]]]
            oprs.append(opr)
        else:
            while oprs and cls._GetPrecedence(oprs[-1]) >= prec :
                cls._EvaluateOperatorBack(opds, oprs)
            if opr:
                oprs.append(opr)

    @classmethod
    def _ProcessOperator(cls, is_start, opds, oprs, token):
        rows = len(opds)
        token = token.lower()
        if token == u"-":
            token = u"--" if is_start else u"-"
        elif token == u"=":
            token = u"=="
        cls._EvaluateOperator(opds, oprs, token)

    @classmethod
    def EvaluateExpression(cls, table, expr):
        rows = len(table)
        opds = []
        oprs = []
        for _ in range(rows):
            opds.append([])
        reading = None  # None = nothing, 0 = operator, 1 = field tokens (can be operator too), 2 = number, 3 = string
        is_start = True
        is_escaping = False
        string_ch = None
        token = u""
        expr += u" "  # add a terminating character (to end token parsing)
        for idx, ch in enumerate(expr):
            if reading == 3:  # string
                if is_escaping:
                    # unescape characters
                    token += util.Unescape(ch)
                    is_escaping = False
                elif ch == "\\":
                    is_escaping = True
                elif ch == string_ch:
                    for i in range(rows):
                        opds[i].append(token)
                    token = u""
                    string_ch = None
                    reading = None
                else:
                    token += ch
            elif reading == 2:  # number
                if cls._IsNumericCharacter(ch):
                    token += ch
                else:
                    num = float(token) if u"." in token else int(token)
                    for i in range(rows):
                        opds[i].append(num)
                    token = u""
                    if cls._IsOperatorCharacter(ch):
                        reading = 0
                        token = ch
                        if ch in (u"(", u","):
                            is_start = True
                    else:
                        reading = None
            elif reading == 1:
                if cls._IsFieldTokenCharacter(ch):
                    token += ch
                else:
                    if token.lower() in df.OPERATOR_TOKENS:
                        cls._ProcessOperator(is_start, opds, oprs, token)
                        token = u""
                        if ch.isspace():
                            reading = None
                        else:
                            token = ch
                            if ch in (u"\"", "\'"):
                                reading = 3
                                token = u""
                                string_ch = ch
                            elif cls._IsNumericCharacter(ch):
                                reading = 2
                            elif cls._IsFieldTokenCharacter(ch):
                                reading = 1
                            elif cls._IsOperatorCharacter(ch):
                                reading = 0
                                if ch in (u"(", u","):
                                    is_start = True
                    elif ch == u"(":  # function
                        oprs.append(token)
                        oprs.append(ch)
                        idx2 = idx + 1
                        while idx2 < len(expr) and expr[idx2] == u" ":
                            idx2 = idx2 + 1
                        if idx2 < len(expr) and expr[idx2] == u")":
                            for i in range(rows):
                                opds[i].append(None)
                        is_start = True
                        token = u""
                        reading = None
                    else:
                        vals = table.GetVals(token)
                        for i in range(rows):
                            opds[i].append(vals[i])
                        token = u""
                        if cls._IsOperatorCharacter(ch):
                            reading = 0
                            token = ch
                            if ch in (u"(", u","):
                                is_start = True
                        else:
                            reading = None
            elif reading == 0:
                if token == u"":
                    is_opr = True
                elif token in (u"(", u")", u",", u"+", u"-", u"*", u"/", u"%"):
                    is_opr = False  # just to terminate the current segment
                elif token and ch == u"(":  # r".+\(" cannot be an operator
                    is_opr = False
                elif token.isalpha():
                    is_opr = ch.isalpha()
                else:
                    is_opr = (not ch.isalnum()) and (not ch.isspace())

                if is_opr:
                    token += ch
                else:
                    cls._ProcessOperator(is_start, opds, oprs, token)
                    token = u""
                    if ch.isspace():
                        reading = None
                    else:
                        token = ch
                        if ch in (u"\"", "\'"):
                            reading = 3
                            token = u""
                            string_ch = ch
                        elif cls._IsNumericCharacter(ch) or (ch == u"-" and is_start):
                            reading = 2
                        elif cls._IsFieldTokenCharacter(ch):
                            reading = 1
                        elif cls._IsOperatorCharacter(ch):
                            reading = 0
                        is_start = ch in (u"(", u",")

            else:  # None
                if ch.isspace():
                    reading = None
                else:
                    token += ch
                    if ch in (u"\"", u"\'"):
                        reading = 3
                        token = u""
                        string_ch = ch
                    elif cls._IsNumericCharacter(ch) or (ch == u"-" and is_start):
                        reading = 2
                    elif cls._IsFieldTokenCharacter(ch):
                        reading = 1
                    elif cls._IsOperatorCharacter(ch):
                        reading = 0
                    is_start = ch in (u"(", u",")
        cls._EvaluateOperator(opds, oprs)  # opr = None
        return [row[0] for row in opds]

    @classmethod
    def EvaluateExpressions(cls, table, exprs):
        ret = tb.SgTable()
        ret.SetFields(exprs)
        rows = len(table)
        for _ in range(rows):
            ret.Append([])
        for expr in exprs:
            res = cls.EvaluateExpression(table, expr)
            for i, val in enumerate(res):
                # TODO(lnishan): Fix the cheat here.
                ret._table[i].append(val)
        return ret
