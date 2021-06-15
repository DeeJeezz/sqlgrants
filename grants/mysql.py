import enum
import re
from collections import namedtuple

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

RE_GRANT = re.compile(r'GRANT (?P<privileges>.*) ON (?P<schema>\S*)\.(?P<table>\S*)')


class GrantLevel(enum.Enum):
    TABLE = enum.auto()
    SCHEMA = enum.auto()
    GLOBAL = enum.auto()


class Privileges(enum.Enum):
    ALL = 'ALL PRIVILEGES'
    DELETE = 'DELETE'
    INSERT = 'INSERT'
    SELECT = 'SELECT'
    UPDATE = 'UPDATE'
    USAGE = 'USAGE'

    def __repr__(self):
        return self.value


Grants = namedtuple('Grants', ['privileges', 'schema', 'table'])


class MySQLGrant:
    def __init__(self, engine: Engine, username: str = '', host: str = '%'):
        self._engine = engine
        self._username = username or engine.url.username
        self._host = host
        self._grants = {key: [] for key in GrantLevel}
        self._update_grants()

    def _get_grants(self) -> list:
        try:
            with Session(self._engine) as session:
                query = session.execute(f'SHOW GRANTS FOR {self._username}')
                return query.all()
        except Exception as e:
            raise e

    def _update_grants(self) -> None:
        for grant in self._get_grants():
            match = RE_GRANT.match(grant[0])
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

                grants = Grants(privileges, schema, table)
                self._grants[level].append(grants)

    def check_permissions(self, schema: str = '*', table: str = '*') -> set:
        result = set()

        for grant_level in GrantLevel:
            grant: Grants
            for grant in self._grants[grant_level]:
                if grant.schema in ('*', schema) and grant.table in ('*', table):
                    set.update(result, [Privileges(p) for p in grant.privileges])

        if Privileges.ALL in result:
            return {Privileges.ALL}

        if len(result) > 1:
            result.discard(Privileges.USAGE)

        return result
