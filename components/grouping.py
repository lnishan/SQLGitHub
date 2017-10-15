"""Group and generate a list of SgTable's."""

import table as tb


class SgGrouping:
    """Group and generate a list of SgTable's."""

    @staticmethod
    def GenerateGroups(table, groups):
        num_groups = len(groups)
        groups_dict = {}
        for row in table:
            key = tuple(row[-num_groups:])
            if not groups_dict.has_key(key):
                groups_dict[key] = tb.SgTable()
                groups_dict[key].SetFields(table.GetFields()[:-num_groups])
            groups_dict[key].Append(row[:-num_groups])
        return groups_dict.values()
