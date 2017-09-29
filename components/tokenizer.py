"""Tokenizer for SQLGitHub.

Sample Usage:
    print(SgTokenizer.Tokenize("Select name, description from abeil.repos"))
"""


class SgTokenizer:
    """Tokenizer for SQLGitHub."""

    _RESERVED_TOKENS = ["select", "from", "where", "group", "order"]  # modify components/parser.py also

    @staticmethod
    def Tokenize(sql):
        return [token.lower() if token.lower() in SgTokenizer._RESERVED_TOKENS else token for token in sql.split(" ")]
