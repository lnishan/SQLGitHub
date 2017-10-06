"""A class for SQLGitHub sessions.

Sample Usage:
    g = Github(token)
    s = SgSession(g, ["name", "description"], "abseil.repos")
    print(s.Execute())
"""

import table as tb
import table_fetcher
import expression


# TODO(lnishan): Change it to SgSessionSimple and add SgSession to handle unions and joins.
class SgSession:
    """A class for SQLGitHub sessions."""

    def __init__(self, github, field_exprs, source, condition=None):
        self._field_exprs = field_exprs
        self._source = source
        self._condition = condition

        # TODO(lnishan): Take expressions in self._condition into account
        rel_keys = expression.SgExpression.ExtractTokensFromExpressions(self._field_exprs)
        self._fetcher = table_fetcher.SgTableFetcher(github, rel_keys)

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
        return expression.SgExpression.EvaluateExpressions(filtered_table, self._field_exprs)
