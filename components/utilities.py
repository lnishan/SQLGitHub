"""Utilities for general operations."""


def PrintResult(table, output):
    if output == "str":
        print(table)
    elif output == "csv":
        print(table.InCsv())
    elif output == "html":
        print(table.InHtml())

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

def Unescape(ch):
    if ch == "0":
        return chr(0)
    elif ch == "\'":
        return "\'"
    elif ch == "\"":
        return "\""
    elif ch == "b":
        return "\b"
    elif ch == "n":
        return "\n"
    elif ch == "r":
        return "\r"
    elif ch == "t":
        return "\t"
    elif ch == "Z":
        return chr(26)
    elif ch == "\\":
        return "\\"
    elif ch == "%":  # keep escape: like <literal string>
        return "\\%"
    elif ch == "_":
        return "\\_"
