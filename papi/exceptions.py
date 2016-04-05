class PAPIException(Exception):
    pass


class PAPIMaintenance(PAPIException):
    pass


class PAPIAuthException(PAPIException):
    pass


class PAPIAuthFailed(PAPIAuthException):
    pass


class PAPIAuthExpired(PAPIAuthException):
    pass
