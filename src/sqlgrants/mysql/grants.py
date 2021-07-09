import enum
from collections import namedtuple

Grants: namedtuple = namedtuple('Grants', ['privileges', 'schema', 'table'])


class GrantType(enum.Enum):
    ALL = 'ALL PRIVILEGES'
    ALTER = 'ALTER'
    ALTER_ROUTINE = 'ALTER ROUTINE'
    CREATE = 'CREATE'
    CREATE_ROLE = 'CREATE ROLE'
    CREATE_ROUTINE = 'CREATE ROUTINE'
    CREATE_TABLESPACE = 'CREATE TABLESPACE'
    CREATE_TEMPORARY_TABLES = 'CREATE TEMPORARY TABLES'
    CREATE_USER = 'CREATE USER'
    CREATE_VIEW = 'CREATE VIEW'
    DELETE = 'DELETE'
    DROP = 'DROP'
    DROP_ROLE = 'DROP ROLE'
    EVENT = 'EVENT'
    EXECUTE = 'EXECUTE'
    FILE = 'FILE'
    GRANT_OPTION = 'GRANT OPTION'
    INDEX = 'INDEX'
    INSERT = 'INSERT'
    LOCK_TABLES = 'LOCK TABLES'
    PROCESS = 'PROCESS'
    PROXY = 'PROXY'
    REFERENCES = 'REFERENCES'
    RELOAD = 'RELOAD'
    REPLICATION_CLIENT = 'REPLICATION CLIENT'
    SELECT = 'SELECT'
    SHOW_DATABASES = 'SHOW DATABASES'
    SHOW_VIEW = 'SHOW VIEW'
    SHUTDOWN = 'SHUTDOWN'
    SUPER = 'SUPER'
    TRIGGER = 'TRIGGER'
    UPDATE = 'UPDATE'
    USAGE = 'USAGE'

    @classmethod
    def values(cls) -> list:  # pragma: no cover
        return [key.value for key in cls]

    @classmethod
    def names(cls) -> list:  # pragma: no cover
        return [key.name for key in cls]

    def __repr__(self):  # pragma: no cover
        return self.value


class GrantLevel(enum.Enum):
    TABLE = enum.auto()
    SCHEMA = enum.auto()
    GLOBAL = enum.auto()

    def __repr__(self):  # pragma: no cover
        return f'<{self.__class__.__name__}: {self.name}>'
