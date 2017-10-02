import sys
import time

from github import Github
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from pygments.lexers.sql import SqlLexer

import definition
import parser
import tokenizer


class SQLGitHub:
    """Meta Component for SQLGitHub."""

    _PROMPT_STR = u"SQLGitHub> "

    def __init__(self, token):
        self._github = Github(token)
        self._parser = parser.SgParser(self._github)
        self._completer = WordCompleter(definition.ALL_TOKENS,
                                        ignore_case=True)

    def Execute(self, sql, measure_time=True):
        if measure_time:
            start_time = time.time()
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
            print("-")
            print("Total rows: %d" % (len(result)))
            if measure_time:
                print("Total execution time: %.3fs" % (time.time() - start_time))
        

    def Start(self):
        while True:
            sql = prompt(self._PROMPT_STR,
                         history=FileHistory("history.txt"),
                         auto_suggest=AutoSuggestFromHistory(),
                         completer=self._completer,
                         lexer=SqlLexer)
            if sql.lower() in definition.EXIT_TOKENS:
                break
            self.Execute(sql)
