import sys


if sys.version_info[0] == 2:
    string_types = basestring,
else:
    string_types = str,


def atoi(string, default=0):
    if (isinstance(string, int)):
        return string

    try:
        return int(string)
    except (TypeError, ValueError):
        return default
