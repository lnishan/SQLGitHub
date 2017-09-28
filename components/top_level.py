from github import Github


class SQLGitHub:
    """Meta Component for SQLGitHub."""

    def __init__(self, token):
        self._github = Github(token)
