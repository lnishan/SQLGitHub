from components import core

try:
    import config
except ImportError:
    token = None
else:
    token = config.token


if __name__ == "__main__":
    token = token or raw_input("Please enter your GitHub token (which can be obtained from https://github.com/settings/tokens):")
    sqlserv = core.SQLGitHub(token)
    org = sqlserv._github.get_organization("google")
    for repo in org.get_repos():
        print(repo.name)
