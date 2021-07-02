from sqlalchemy.exc import DBAPIError


class SQLAlchemyExceptionMixin:
    def __init__(self, e: DBAPIError):
        super().__init__(e.statement, e.params, e.orig)


class AccessDenied(SQLAlchemyExceptionMixin, DBAPIError):
    pass


class ConnectionRefused(SQLAlchemyExceptionMixin, DBAPIError):
    pass


class BadRequest(SQLAlchemyExceptionMixin, DBAPIError):
    pass


class NotFoundError(Exception):
    pass
