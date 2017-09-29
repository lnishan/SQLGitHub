import sys

from github import Github
import tokenizer
import parser


class SQLGitHub:
    """Meta Component for SQLGitHub."""

    _PROMPT_STR = "SQLGitHub> "

    def __init__(self, token):
        self._github = Github(token)
        self._parser = parser.SgParser(self._github)

    def Start(self):
        while True:
            sys.stdout.write(self._PROMPT_STR)
            sys.stdout.flush()
            sql = sys.stdin.readline().strip()
            if sql in ["q", "exit"]:
                break
            tokens = tokenizer.SgTokenizer.Tokenize(sql)
            try:
                session = self._parser.Parse(tokens)
            except NotImplementedError:
                sys.stderr.write("Not implemented command tokens in SQL.\n")
            except SyntaxError:
                sys.stderr.write("SQL syntax incorrect.\n")
            else:
                result = session.Execute()
                print(result)
