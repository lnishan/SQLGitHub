"""Parser for SQLGitHub. Outputs SgSession.

Sample Usage:
    g = Github(token)
    parser = SgParser(g)
    s = parser.Parse(["select", "name,", "description", "from", "abseil.repos"])
    print(s.Execute())
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
        self._field_exprs = []
        self._source = None
        self._condition = None

    def _ParseSelect(self, sub_tokens):
        sub_tokens_str = u" ".join(sub_tokens)
        in_string = False
        in_bracket = False
        is_escaping = False
        expr = u""
        for ch in sub_tokens_str:
            if in_string:
                expr += ch
                if is_escaping:
                    is_escaping = False
                elif ch == "\\":
                    is_escaping = True
                elif ch in (u"\'", u"\""):
                    in_string = False
            elif in_bracket:
                expr += ch
                if ch == u")":
                    in_bracket = False
            else:
                if ch == u",":
                    self._field_exprs.append(expr.strip())
                    expr = u""
                else:
                    expr += ch
                    if ch in (u"\'", u"\""):
                        in_string = True
                        is_escaping = False
                    elif ch == u"(":
                        in_bracket = True
        if expr:
            self._field_exprs.append(expr.strip())

    def _ParseFrom(self, sub_tokens):
        # TODO(lnishan): Handle sub-queries (by creating another SgParser instance) here
        self._source = sub_tokens[0]

    def _ParseWhere(self, sub_tokens):
        self._condition = u" ".join(sub_tokens)

    def _ParseGroup(self, sub_tokens):
        pass

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
        return session.SgSession(self._github, self._field_exprs, self._source, self._condition)
