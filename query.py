#!/usr/bin/env python

import argparse

import config_loader
from components import top_level
from components import utilities as util

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("sql", type=unicode, help="a line of sql for query")
args = arg_parser.parse_args()


if __name__ == "__main__":
    token, output = config_loader.Load("config")
    sqlserv = top_level.SQLGitHub(token, output)
    result, exec_time = sqlserv.Execute(args.sql, display_result=False)
    util.PrintResult(result, output)
