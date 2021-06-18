from sqlalchemy.exc import DBAPIError


class AccessDenied(DBAPIError):
    def __init__(self, e: DBAPIError):
        super().__init__(e.statement, e.params, e.orig)


class ConnectionRefused(DBAPIError):
    def __init__(self, e: DBAPIError):
        super().__init__(e.statement, e.params, e.orig)


class BadRequest(DBAPIError):
    def __init__(self, e: DBAPIError):
        super().__init__(e.statement, e.params, e.orig)
