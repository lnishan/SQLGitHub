"""Parser for SQLGitHub. Outputs SgSession.

Sample Usage:
    g = Github(token)
    parser = SgParser(g)
    s = parser.Parse(["select", "name,", "description", "from", "abseil.repos"])
    print(s.Execute())
    print(parser._ParseOrder(["by", "a+b", "DESC,", "c", "-", "b", "ASC", ",", "a%b"]))
"""

import definition
import session


# TODO(lnishan): Change it to SgParseSimple, modify tokenizer and add SgParser to handle unions and joins.
class SgParser:
    """Parser for SQLGitHub. Outputs SgSession."""
    
    def __init__(self, github):
        self._github = github
        self._Initialize()

    def _Initialize(self):
        self._field_exprs = None
        self._source = None
        self._condition = None
        self._orders = None

    def __GetCommaSeparatedExprs(self, tokens_str):
        exprs = []
        in_string = False
        bracket_sum = 0
        is_escaping = False
        expr = u""
        for ch in tokens_str:
            if in_string:
                expr += ch
                if is_escaping:
                    is_escaping = False
                elif ch == "\\":
                    is_escaping = True
                elif ch in (u"\'", u"\""):
                    in_string = False
            elif bracket_sum > 0:
                expr += ch
                if ch == "\"":
                    in_string = True
                elif ch == u"(":
                    bracket_sum = bracket_sum + 1
                elif ch == u")":  # and not in_string
                    bracket_sum = bracket_sum - 1
            else:
                if ch == u",":
                    exprs.append(expr.strip())
                    expr = u""
                else:
                    expr += ch
                    if ch in (u"\'", u"\""):
                        in_string = True
                        is_escaping = False
                    elif ch == u"(":
                        bracket_sum = 1
        if expr:
            exprs.append(expr.strip())
        return exprs

    def _ParseSelect(self, sub_tokens):
        sub_tokens_str = u" ".join(sub_tokens)
        self._field_exprs = self.__GetCommaSeparatedExprs(sub_tokens_str)

    def _ParseFrom(self, sub_tokens):
        # TODO(lnishan): Handle sub-queries (by creating another SgParser instance) here
        self._source = sub_tokens[0]

    def _ParseWhere(self, sub_tokens):
        self._condition = u" ".join(sub_tokens)

    def _ParseGroup(self, sub_tokens):
        pass

    def _ParseOrder(self, sub_tokens):
        self._orders = [[], []]
        sub_tokens_str = u" ".join(sub_tokens[1:])  # get rid of "by"
        raw_exprs = self.__GetCommaSeparatedExprs(sub_tokens_str)
        for raw_expr in raw_exprs:
            if raw_expr.lower().endswith(u" asc"):
                self._orders[0].append(raw_expr[:-4])
                self._orders[1].append(1)
            elif raw_expr.lower().endswith(u" desc"):
                self._orders[0].append(raw_expr[:-5])
                self._orders[1].append(-1)
            else:
                self._orders[0].append(raw_expr)
                self._orders[1].append(1)

    def _ParseCmdToken(self, cmd_token, sub_tokens):
        if cmd_token == u"select":
            self._ParseSelect(sub_tokens)
        elif cmd_token == u"from":
            self._ParseFrom(sub_tokens)
        elif cmd_token == u"where":
            self._ParseWhere(sub_tokens)
        elif cmd_token == u"group":
            self._ParseGroup(sub_tokens)
        elif cmd_token == u"order":
            self._ParseOrder(sub_tokens)
        else:
            raise NotImplementedError("Command token not implemented.")
    
    def Parse(self, tokens):
        self._Initialize()
        cmd_token = None
        sub_tokens = []
        for token in tokens:
            if token in definition.COMMAND_TOKENS:
                if cmd_token:
                    self._ParseCmdToken(cmd_token, sub_tokens)
                cmd_token = token
                sub_tokens = []
            else:
                sub_tokens.append(token)
        if cmd_token:
            self._ParseCmdToken(cmd_token, sub_tokens)
        if not self._field_exprs or not self._source:
            raise SyntaxError("SQL syntax incorrect.")
        return session.SgSession(self._github, self._field_exprs, self._source, self._condition, self._orders)
