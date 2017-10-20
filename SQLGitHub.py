#!/usr/bin/env python

import config_loader
from components import top_level


if __name__ == "__main__":
    token, output = config_loader.Load("config")
    sqlserv = top_level.SQLGitHub(token, output)
    sqlserv.Start()
