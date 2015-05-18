def atoi(string, default=0):
    if (isinstance(string, int)):
        return string

    try:
        return int(string)
    except (TypeError, ValueError):
        return default
