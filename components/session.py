"""A class for SQLGitHub sessions.

Sample Usage:
    g = Github(token)
    s = SgSession(g, ["name", "description"], "abseil.repos")
    print(s.Execute())
"""

import table as tb
import table_fetcher
import expression_evaluator


class SgSession:
    """A class for SQLGitHub sessions."""

    def __init__(self, github, field_exprs, source, condition=None):
        self._fetcher = table_fetcher.SgTableFetcher(github)
        self._field_exprs = field_exprs
        self._source = source
        self._condition = condition

    def Execute(self):
        # source is either a label (eg. "google.issues") or a SgSession
        source_table = self._source.Execute() if isinstance(self._source, SgSession) else self._fetcher.Fetch(self._source)
        if self._condition:
            filtered_table = tb.SgTable()
            filtered_table.SetFields(source_table.GetFields())
            for row in source_table:
                if self._condition.Evaluate(source_table.GetFields(), row):
                    filtered_table.Append(row)
        else:
            filtered_table = source_table
        return expression_evaluator.SgExpressionEvaluator.EvaluateExpressionsInTable(filtered_table, self._field_exprs)
