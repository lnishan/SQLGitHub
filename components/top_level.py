import sys
import time

from github import Github
from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import style_from_pygments
from pygments.lexers.sql import MySqlLexer
from pygments.styles.monokai import MonokaiStyle

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
        self._style = style_from_pygments(MonokaiStyle)

    def Execute(self, sql, measure_time=True):
        if not sql:
            return
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
            if False:
                pass
            else:
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
                         lexer=MySqlLexer,
                         style=self._style,
                         on_abort=AbortAction.RETRY)
            if sql.lower() in definition.EXIT_TOKENS:
                break
            self.Execute(sql)
