"""A class for SQLGitHub sessions.

Sample Usage:
    g = Github(token)
    s = SgSession(g, ["name", "description"], "abseil.repos")
    print(s.Execute())
"""

import table as tb
import table_fetcher
from expression import SgExpression
from grouping import SgGrouping
from ordering import SgOrdering
from ordering import SgTableOrdering


# TODO(lnishan): Change it to SgSessionSimple and add SgSession to handle unions and joins.
class SgSession:
    """A class for SQLGitHub sessions."""

    def __init__(self, github, field_exprs, source, condition=None, groups=None, having=None, orders=None, limit=None):
        self._field_exprs = field_exprs
        self._source = source
        self._condition = condition
        self._groups = groups
        self._having = having
        self._orders = orders
        self._limit = limit

        rel_keys = SgExpression.ExtractTokensFromExpressions(self._field_exprs)
        if self._condition:
            rel_keys += SgExpression.ExtractTokensFromExpressions([self._condition])
        if self._groups:
            rel_keys += SgExpression.ExtractTokensFromExpressions(self._groups)
        if self._having:
            rel_keys += SgExpression.ExtractTokensFromExpressions([self._having])
        if self._orders:
            rel_keys += SgExpression.ExtractTokensFromExpressions(self._orders[0])
        rel_keys = list(set(rel_keys))
        self._fetcher = table_fetcher.SgTableFetcher(github, rel_keys)

    def _GetEmptyTable(self):
        table = tb.SgTable()
        table.SetFields(self._field_exprs)
        return table

    def Execute(self):
        # source is either a label (eg. "google.issues") or a SgSession
        source_table = self._source.Execute() if isinstance(self._source, SgSession) else self._fetcher.Fetch(self._source)
        if not source_table[:]:
            return self._GetEmptyTable()

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
        if not filtered_table[:]:
            return self._GetEmptyTable()
        
        # evaluate all necessary expressions
        # in reversed order because we process from the rightmost item first
        select_tokens = SgExpression.ExtractTokensFromExpressions(self._field_exprs[:]) 
        eval_exprs = select_tokens
        if self._orders:
            order_tokens = SgExpression.ExtractTokensFromExpressions(self._orders[0])
            eval_exprs += order_tokens
        if self._having:
            having_tokens = SgExpression.ExtractTokensFromExpressions([self._having])
            eval_exprs += having_tokens
        if self._groups:
            eval_exprs += self._groups
        res_table = SgExpression.EvaluateExpressions(filtered_table, eval_exprs)

        # group by
        if self._groups:
            res_tables = SgGrouping.GenerateGroups(res_table, self._groups)
        else:
            res_tables = [res_table]

        # having
        if self._having:
            filtered_tables = []
            for table in res_tables:
                if all(SgExpression.EvaluateExpression(table, self._having)):
                    filtered_tables.append(table.SliceCol(0, len(table.GetFields()) - len(having_tokens)))
            res_tables = filtered_tables

        # order by
        if self._orders:
            for table in res_tables:
                table.Copy(table.SliceCol(0, len(table.GetFields()) - len(order_tokens)).Chain(SgExpression.EvaluateExpressions(table, self._orders[0])))
                ordering = SgOrdering(table, self._orders[1])
                table.Copy(ordering.Sort(keep_order_fields=True))
            ordering = SgTableOrdering(res_tables, self._orders[1])
            res_tables = ordering.Sort()

        # TODO(lnishan): Support having here

        # process select
        for table in res_tables:
            table.Copy(SgExpression.EvaluateExpressions(table, self._field_exprs))

        # check if all tokens in expressions are contained in aggregate functions
        check_exprs = [expr for expr in self._field_exprs if expr not in self._groups] if self._groups else self._field_exprs
        if SgExpression.IsAllTokensInAggregate(check_exprs):
            for table in res_tables:
                table = table.SetTable([table[0]])

        merged_table = tb.SgTable()
        merged_table.SetFields(res_tables[0].GetFields())
        for table in res_tables:
            for row in table:
                merged_table.Append(row)

        # process limit
        if self._limit:
            merged_table.SetTable(merged_table[:self._limit])

        return merged_table
