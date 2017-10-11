"""A class for SQLGitHub sessions.

Sample Usage:
    g = Github(token)
    s = SgSession(g, ["name", "description"], "abseil.repos")
    print(s.Execute())
"""

import table as tb
import table_fetcher
from expression import SgExpression
from ordering import SgOrdering


# TODO(lnishan): Change it to SgSessionSimple and add SgSession to handle unions and joins.
class SgSession:
    """A class for SQLGitHub sessions."""

    def __init__(self, github, field_exprs, source, condition=None, orders=None):
        self._field_exprs = field_exprs
        self._source = source
        self._condition = condition
        self._orders = orders

        rel_keys = SgExpression.ExtractTokensFromExpressions(self._field_exprs)
        if self._condition:
            rel_keys += SgExpression.ExtractTokensFromExpressions([self._condition])
        if self._orders:
            rel_keys += SgExpression.ExtractTokensFromExpressions(self._orders[0])
        rel_keys = list(set(rel_keys))
        self._fetcher = table_fetcher.SgTableFetcher(github, rel_keys)

    def Execute(self):
        # source is either a label (eg. "google.issues") or a SgSession
        source_table = self._source.Execute() if isinstance(self._source, SgSession) else self._fetcher.Fetch(self._source)

        # evaluate where
        if self._condition:
            filtered_table = tb.SgTable()
            filtered_table.SetFields(source_table.GetFields())
            meets = SgExpression.EvaluateExpression(source_table, self._condition)
            for i, row in enumerate(source_table):
                if meets[i]:
                    filtered_table.Append(row)
        else:
            filtered_table = source_table
        
        # evaluate all necessary expressions
        eval_exprs = self._field_exprs[:]
        if self._orders:
            eval_exprs += self._orders[0]
        res_table = SgExpression.EvaluateExpressions(filtered_table, eval_exprs)

        # sort and remove columns for sorting
        if self._orders:
            ordering = SgOrdering(res_table, self._orders[1])
            res_table = ordering.Sort(0, len(res_table)-1).SliceCol(0, len(self._field_exprs))

        # check if all tokens in expressions are contained in aggregate functions
        if SgExpression.IsAllTokensInAggregate(self._field_exprs):
            res_table = res_table[0]

        return res_table
