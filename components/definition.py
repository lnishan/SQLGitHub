"""Language definitions for SQLGitHub."""


COMMAND_TOKENS = [u"select", u"from", u"where", u"group", u"having", u"order", u"limit"]
EXIT_TOKENS = [u"exit", u"q"]
OPERATOR_TOKENS = [u"interval",
                   u"binary", u"collate",
                   u"!",
                   u"-", u"~",
                   u"^",
                   u"*", u"/", u"div", u"%", u"mod",
                   u"-", u"+",
                   u"<<", u">>",
                   u"&",
                   u"|",
                   u"=", u"<=>", u">=", u">", u"<=", u"<", u"<>", u"!=", u"is", u"like", u"regexp", u"in",
                   u"between", u"case", u"when", u"then", u"else",
                   u"not",
                   u"and", u"&&",
                   u"xor",
                   u"or", u"||",
                   u"=", u":=",
                   u",",
                   u"(",
                   u")"]

AGGREGATE_FUNCTIONS = ["avg", "count", "max", "min", "sum"]
HORIZONTAL_FUNCTIONS = ["abs", "ceil", "ceiling", "exp", "floor", "greatest", "least", "ln", "log", "pow", "power", "sign", "sqrt", "ascii", "concat", "concat_ws", "find_in_set", "insert", "instr", "length", "locate", "lcase", "lower", "left", "mid", "repeat", "right", "replace", "strcmp", "substr", "substring", "ucase", "upper", "curdate", "current_date", "current_time", "current_timestamp", "curtime", "localtime", "localtimestamp", "now", "bin"]

ALL_TOKENS = (COMMAND_TOKENS +
              EXIT_TOKENS +
              OPERATOR_TOKENS +
              AGGREGATE_FUNCTIONS +
              HORIZONTAL_FUNCTIONS)


PRECEDENCE = {
    u"interval": 17,
    u"binary": 16, u"collate": 16,
    u"!": 15,
    u"--": 14, u"~": 14,  # -- = - (unary minus)
    u"^": 13,
    u"*": 12, u"/": 12, u"div": 12, u"%": 12, u"mod": 12,
    u"-": 11, u"+": 11,
    u"<<": 10, u">>": 10,
    u"&": 9,
    u"|": 8,
    u"==": 7, u"<=>": 7, u">=": 7, u">": 7, u"<": 7, u"<>": 7, u"!=": 7, u"is": 7, u"like": 7, u"regexp": 7, u"in": 7,  # == = = (comparison)
    u"between": 6, u"case": 6, u"when": 6, u"then": 6, u"else": 6,
    u"not": 5,
    u"and": 4, u"&&": 4,
    u"xor": 3,
    u"or": 2, u"||": 2,
    u"=": 1, u":=": 1,
    u",": -1,
    u"(": -2,
    u")": -3}
