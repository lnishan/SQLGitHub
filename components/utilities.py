"""Utilities for general operations."""


def IsNumeric(num_str):
    try:
        val = int(num_str)
    except ValueError:
        return False
    else:
        return True

def GuaranteeUnicode(obj):
    if type(obj) == unicode:
        return obj
    elif type(obj) == str:
        return unicode(obj, "utf-8")
    else:
        return unicode(str(obj), "utf-8")
