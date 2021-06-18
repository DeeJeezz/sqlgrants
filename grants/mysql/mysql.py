import re

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import ProgrammingError, DatabaseError
from sqlalchemy.orm import Session, Query

from grants.exceptions import AccessDenied, ConnectionRefused, BadRequest
from .grants import Grants, GrantType, GrantLevel


class MySQL:
    DIALECT = 'mysql'
    DRIVER = 'mysqlconnector'
    DEFAULT_SCHEMA = 'information_schema'
    RE_GRANT = re.compile(r'GRANT (?P<privileges>.*) ON (?P<schema>\S*)\.(?P<table>\S*)')

    def __init__(self, login: str, password: str, host: str = '127.0.0.1', port: int = 3306):
        self._engine: Engine = self._create_engine(login, password, host, port)

    def _create_engine(self, login: str, password: str, host: str, port: int) -> Engine:
        url: str = f'{self.DIALECT}+{self.DRIVER}://{login}:{password}@{host}:{port}/{self.DEFAULT_SCHEMA}'
        return create_engine(url)

    def _show_grants(self, username: str, host: str) -> dict:
        try:
            with Session(self._engine) as session:
                query: Query = session.execute(f'SHOW GRANTS FOR \'{username}\'@\'{host}\'')
                data: list = query.all()
                return self._process_grant_list(data)
        except ProgrammingError as e:
            err_number = e.orig.errno
            if err_number == 1044:
                raise AccessDenied(e)
            elif err_number == 1141:
                raise BadRequest(e)
            raise e
        except DatabaseError as e:
            raise ConnectionRefused(e)

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
        grants = self._show_grants(username or self._engine.url.username, host)
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
