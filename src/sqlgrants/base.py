from collections import namedtuple
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import DatabaseError, ProgrammingError
from sqlalchemy.orm import Query, Session

from .exceptions import AccessDenied, BadRequest, ConnectionRefused


class BaseDatabase:

    def __init__(self, dialect: str, driver: str, default_schema: str):
        self._dialect = dialect
        self._driver = driver
        self._default_schema = default_schema
        self._engine = None

    def _create_engine_url(self, login: str, password: str, host: str, port: int) -> str:
        return f'{self._dialect}+{self._driver}://{login}:{password}@{host}:{port}/{self._default_schema}'

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, url: str):
        self._engine: Engine = create_engine(url)

    def execute(self, sql: str) -> Optional[list]:
        try:
            with Session(self.engine) as session:
                query: Query = session.execute(sql)
                if query.returns_rows:
                    return query.all()
        except ProgrammingError as e:  # pragma: no cover
            err_number = e.orig.errno
            if err_number == 1044:
                raise AccessDenied(e)
            elif err_number == 1141:
                raise BadRequest(e)
            raise e
        except DatabaseError as e:  # pragma: no cover
            raise ConnectionRefused(e)

    @property
    def schemas(self) -> list:
        schemas: list = self.execute('SHOW DATABASES')
        return [Schema(schema[0], self) for schema in schemas]


Table = namedtuple('Table', ['name', 'schema'])


class Schema:

    def __init__(self, name: str, db: BaseDatabase):
        self.name: str = name
        self._db: BaseDatabase = db

    @property
    def tables(self):
        tables: list = self._db.execute(f'SHOW TABLES FROM {self.name}')
        return [Table(name=table[0], schema=self.name) for table in tables]
