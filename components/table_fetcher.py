"""Fetches data from GitHub API, store and return the data in a SgTable.

Sample Usage:
    sqlserv = top_level.SQLGitHub(token)
    fetcher = SgTableFetcher(sqlserv._github)
    print(fetcher.Fetch("abseil"))
    print("----------------------------")
    print(fetcher.Fetch("abseil.repos"))
    print("----------------------------")
    print(fetcher.Fetch("abseil.issues"))
    print("----------------------------")
"""

import datetime
import inspect

from github.NamedUser import NamedUser

import table as tb
import utilities as util


class SgTableFetcher:
    """Fetches data from GitHub API, store and return the data in a SgTable."""

    def __init__(self, github, rel_keys=None):
        self._github = github
        self._rel_keys = rel_keys

    def _Parse(self, label):
        tmp = label.split(".")
        if len(tmp) == 1:  # no dots
            return label, None, None
        elif len(tmp) == 2:
            return tmp[0], tmp[1], None
        else:
            return tmp[0], tmp[1], tmp[2:]

    def _GetKeys(self, cls):
        if self._rel_keys:
            # TODO(lnishan): Might want to check for existence of every key in self._rel_keys
            return self._rel_keys
        else:
            return [unicode(key, "utf-8") for key, val in inspect.getmembers(cls, lambda m: not inspect.ismethod(m)) if not key.startswith("_")]

    def __ConvertVal(self, val):
        if isinstance(val, NamedUser):
            return val.login
        else:
            return val

    def _GetVals(self, cls):
        if self._rel_keys:
            return [self.__ConvertVal(getattr(cls, key)) for key in self._rel_keys]
        else:
            ret = [self.__ConvertVal(val) for key, val in inspect.getmembers(cls, lambda m: not inspect.ismethod(m)) if not key.startswith("_")]
    
    def Fetch(self, label):
        ret = tb.SgTable()
        org_name, sub_name, add_info = self._Parse(label)
        org = self._github.get_organization(org_name)
        if sub_name == None:  # eg. "google"
            ret.SetFields(self._GetKeys(org))
            ret.Append(self._GetVals(org))
        elif sub_name == u"repos":
            repos = org.get_repos()
            for repo in repos:
                if not ret.GetFields():
                    ret.SetFields(self._GetKeys(repo))
                ret.Append(self._GetVals(repo))
        elif sub_name == u"issues":
            days = None
            state = u"open"
            if add_info:
                for info in add_info:
                    if util.IsNumeric(info):
                        days = int(info)
                    elif info in (u"all", u"open", u"closed"):
                        state = info
            repos = org.get_repos()
            for repo in repos:
                issues = repo.get_issues(state=state, since=datetime.datetime.now() - datetime.timedelta(days=days)) if days else repo.get_issues(state=state)
                for issue in issues:
                    if not ret.GetFields():
                        ret.SetFields(self._GetKeys(issue))
                    ret.Append(self._GetVals(issue))
        elif sub_name == u"pulls":
            state = u"open"
            if add_info:
                for info in add_info:
                    if info in (u"all", u"open", u"closed"):
                        state = info
            repos = org.get_repos()
            for repo in repos:
                pulls = repo.get_pulls(state=state)
                for pull in pulls:
                    if not ret.GetFields():
                        ret.SetFields(self._GetKeys(pull))
                    ret.Append(self._GetVals(pull))
        elif sub_name == "commits":
            days = None
            if add_info:
                for info in add_info:
                    if util.IsNumeric(info):
                        days = int(info)
            repos = org.get_repos()
            for repo in repos:
                commits = repo.get_commits(since=datetime.datetime.now() - datetime.timedelta(days=days)) if days else repo.get_commits()
                for commit in commits:
                    if not ret.GetFields():
                        ret.SetFields(self._GetKeys(commit))
                    ret.Append(self._GetVals(commit))
        return ret
