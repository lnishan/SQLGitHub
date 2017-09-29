"""Parser for SQLGitHub. Outputs SgSession.

Sample Usage:
    g = Github(token)
    parser = SgParser(g)
    s = parser.Parse(["select", "name,", "description", "from", "abseil.repos"])
    print(s.Execute())
"""

import session


# TODO(lnishan): Change it to SgParseSimple, modify tokenizer and add SgParser to handle unions and joins.
class SgParser:
    """Parser for SQLGitHub. Outputs SgSession."""
    _RESERVED_TOKENS = ["select", "from", "where", "group", "order"]

    def __init__(self, github):
        self._github = github
        self._Initialize()

    def _Initialize(self):
        self._field_exprs = []
        self._source = None
        self._condition = None

    def _ParseSelect(self, sub_tokens):
        sub_tokens_str = "".join(sub_tokens)
        self._field_exprs = sub_tokens_str.split(",")

    def _ParseFrom(self, sub_tokens):
        # TODO(lnishan): Handle sub-queries (by creating another SgParser instance) here
        self._source = sub_tokens[0]

    def _ParseWhere(self, sub_tokens):
        pass

    def _ParseGroup(self, sub_tokens):
        pass

    def _ParseCmdToken(self, cmd_token, sub_tokens):
        if cmd_token == "select":
            self._ParseSelect(sub_tokens)
        elif cmd_token == "from":
            self._ParseFrom(sub_tokens)
        elif cmd_token == "where":
            self._ParseWhere(sub_tokens)
        elif cmd_token == "group":
            self._ParseGroup(sub_tokens)
        elif cmd_token == "order":
            self._ParseOrder(sub_tokens)
        else:
            raise NotImplementedError("Command token not implemented.")
    
    def Parse(self, tokens):
        self._Initialize()
        cmd_token = None
        sub_tokens = []
        for token in tokens:
            if token in SgParser._RESERVED_TOKENS:
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
