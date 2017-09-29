from components import top_level

try:
    import config
except ImportError:
    token = None
else:
    token = config.token


if __name__ == "__main__":
    token = token or raw_input("Please enter your GitHub token (which can be obtained from https://github.com/settings/tokens):")
    sqlserv = top_level.SQLGitHub(token)
    sqlserv.Start()
