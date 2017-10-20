"""Config loader for SQLGitHub."""

import importlib


def Load(module):
    try:
        mod = importlib.import_module(module)
    except ImportError:
        token = None
        output = "str"
    else:
        token = mod.token if hasattr(mod, "token") else None
        output = mod.output if hasattr(mod, "output") else "str"
    
    token = token or raw_input("Please enter your GitHub token (which can be obtained from https://github.com/settings/tokens): ")

    return (token,
            output)
