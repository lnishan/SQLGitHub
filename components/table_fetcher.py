"""Fetches data from GitHub API, store and return the data in a SgTable.

Sample Usage:
    sqlserv = core.SQLGitHub(token)
    fetcher = table_fetcher.SgTableFetcher(sqlserv._github)
    print(fetcher.Fetch("abseil"))
    print("----------------------------")
    print(fetcher.Fetch("abseil.repos"))
    print("----------------------------")
    print(fetcher.Fetch("abseil.issues"))
    print("----------------------------")
"""

import table
import inspect


class SgTableFetcher:
    """Fetches data from GitHub API, store and return the data in a SgTable."""

    def __init__(self, github):
        self._github = github

    def _Parse(self, label):
        tmp = label.split(".")
        if len(tmp) == 1:  # no dots
            return label, None
        else:
            return tmp[0], tmp[1]

    def _GetKeys(self, cls):
        return [key for key, val in inspect.getmembers(cls, lambda m: not inspect.ismethod(m)) if not key.startswith("_")]

    def _GetVals(self, cls):
        return [val for key, val in inspect.getmembers(cls, lambda m: not inspect.ismethod(m)) if not key.startswith("_")]
    
    def Fetch(self, label):
        ret = table.SgTable()
        org_name, sub_name = self._Parse(label)
        org = self._github.get_organization(org_name)
        if sub_name == None:  # eg. "google"
            ret.SetFields(self._GetKeys(org))
            ret.Append(self._GetVals(org))
        elif sub_name == "repos":
            repos = org.get_repos()
            for repo in repos:
                if not ret.GetFields():
                    ret.SetFields(self._GetKeys(repo))
                ret.Append(self._GetVals(repo))
        elif sub_name == "issues":
            repos = org.get_repos()
            for repo in repos:
                issues = repo.get_issues(state="all")
                for issue in issues:
                    if not ret.GetFields():
                        ret.SetFields(self._GetKeys(repo))
                    ret.Append(self._GetVals(issue))
        return ret
