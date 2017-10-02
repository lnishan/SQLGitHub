"""Tokenizer for SQLGitHub.

Sample Usage:
    print(SgTokenizer.Tokenize("Select name, description from abeil.repos"))
"""

import definition


class SgTokenizer:
    """Tokenizer for SQLGitHub."""

    @staticmethod
    def Tokenize(sql):
        return [token.lower() if token.lower() in definition.COMMAND_TOKENS else token for token in sql.split(" ")]
