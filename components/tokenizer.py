"""Tokenizer for SQLGitHub.

Sample Usage:
    print(SgTokenizer.Tokenize("Select name, description from abeil.repos"))
"""


class SgTokenizer:
    """Tokenizer for SQLGitHub."""

    _RESERVED_TOKENS = [u"select", u"from", u"where", u"group", u"order"]  # modify components/parser.py also

    @staticmethod
    def Tokenize(sql):
        return [unicode(token.lower(), "utf-8") if token.lower() in SgTokenizer._RESERVED_TOKENS else token for token in sql.split(" ")]
