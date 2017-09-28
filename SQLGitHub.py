from components import core
from components import table

try:
    import config
except ImportError:
    token = None
else:
    token = config.token


if __name__ == "__main__":
    table = table.SgTable()
    table.Append([1, 2, 3])
    table.Append([2, 4, 6])
    table.Append([3, 6, 9])
    for row in table:
        print(row)
    print(table[1])
    table[1] = [2, 2, 2]
    print(table[1])
    exit()
    token = token or raw_input("Please enter your GitHub token (which can be obtained from https://github.com/settings/tokens):")
    sqlserv = core.SQLGitHub(token)
    org = sqlserv._github.get_organization("google")
    for repo in org.get_repos():
        print(repo.name)
