"""Utilities for general operations."""


def IsNumeric(num_str):
    try:
        val = int(num_str)
    except ValueError:
        return False
    else:
        return True
