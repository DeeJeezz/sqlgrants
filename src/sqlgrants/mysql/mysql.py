import re
from typing import Optional, Set

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import DatabaseError, ProgrammingError
from sqlalchemy.orm import Query, Session

from sqlgrants.exceptions import AccessDenied, BadRequest, ConnectionRefused

from .grants import GrantLevel, Grants, GrantType


class MySQL:
    DIALECT = 'mysql'
    DRIVER = 'mysqlconnector'
    DEFAULT_SCHEMA = 'information_schema'
    RE_GRANT = re.compile(r'GRANT (?P<privileges>.*) ON (?P<schema>\S*)\.(?P<table>\S*)')

    def __init__(self, login: str, password: str, host: str = '127.0.0.1', port: int = 3306):
        self._login = login
        self._engine: Engine = self._create_engine(login, password, host, port)

    def _create_engine(self, login: str, password: str, host: str, port: int) -> Engine:
        url: str = f'{self.DIALECT}+{self.DRIVER}://{login}:{password}@{host}:{port}/{self.DEFAULT_SCHEMA}'
        return create_engine(url)

    def _execute(self, sql: str) -> Optional[list]:
        try:
            with Session(self._engine) as session:
                query: Query = session.execute(sql)
                if query.returns_rows:
                    return query.all()
        except ProgrammingError as e:
            err_number = e.orig.errno
            if err_number == 1044:
                raise AccessDenied(e)
            elif err_number == 1141:
                raise BadRequest(e)
            raise e
        except DatabaseError as e:
            raise ConnectionRefused(e)

    def _show_grants(self, username: str, host: str) -> dict:
        data: list = self._execute(f'SHOW GRANTS FOR \'{username}\'@\'{host}\'')
        return self._process_grant_list(data)

    def _process_grant_list(self, grant_list: list) -> dict:
        grants = {key: [] for key in GrantLevel}
        for grant in grant_list:
            match = self.RE_GRANT.match(grant[0])
            if match:
                privileges = [p.strip() for p in match.group('privileges').split(',')]
                schema = match.group('schema').strip('`')
                table = match.group('table').strip('`')

                if table != '*':
                    level = GrantLevel.TABLE
                elif schema != '*':
                    level = GrantLevel.SCHEMA
                else:
                    level = GrantLevel.GLOBAL

                grants[level].append(Grants(privileges, schema, table))

        return grants

    def show_grants(self, *, username: str = '', host: str = '%', schema: str = '*', table: str = '*') -> set:
        grants = self._show_grants(username or self._login, host)
        result = set()

        for grant_level in GrantLevel:
            for grant in grants[grant_level]:
                if grant.schema in ('*', schema) and grant.table in ('*', table):
                    set.update(result, [GrantType(p) for p in grant.privileges])

        if GrantType.ALL in result:
            return {GrantType.ALL}

        if len(result) > 1:
            result.discard(GrantType.USAGE)

        return result

    def grant(self, grants: Set[GrantType], *, username: str = '', host: str = '%', schema: str = '*',
              table: str = '*') -> None:
        grant_types: str = ', '.join({grant_type.name for grant_type in grants})
        sql: str = f'GRANT {grant_types} ON {schema}.{table} TO \'{username or self._login}\'@\'{host}\''
        self._execute(sql)

    def revoke(self, grants: Set[GrantType], *, username: str = '', host: str = '%', schema: str = '*',
               table: str = '*') -> None:
        grant_types: str = ', '.join({grant_type.name for grant_type in grants})
        sql: str = f'REVOKE {grant_types} ON {schema}.{table} FROM \'{username or self._login}\'@\'{host}\''
        self._execute(sql)
