import enum
import re
from collections import namedtuple
# from pprint import pprint

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from config import user_engine

RE_GRANT = re.compile(r'GRANT (?P<privileges>.*) ON (?P<schema>\S*)\.(?P<table>\S*)')


class GrantLevel(enum.Enum):
    GLOBAL = enum.auto()
    SCHEMA = enum.auto()
    TABLE = enum.auto()


class Privileges(enum.Enum):
    ALL = 'ALL PRIVILEGES'
    DELETE = 'DELETE'
    INSERT = 'INSERT'
    SELECT = 'SELECT'
    UPDATE = 'UPDATE'
    USAGE = 'USAGE'


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
        grant: Grants
        for grant in self._grants[GrantLevel.TABLE]:
            if grant.schema in ('*', schema) and grant.table in ('*', table):
                set.update(result, grant.privileges)

        for grant in self._grants[GrantLevel.SCHEMA]:
            if grant.schema in ('*', schema) and grant.table in ('*', table):
                set.update(result, grant.privileges)

        for grant in self._grants[GrantLevel.GLOBAL]:
            if grant.schema in ('*', schema) and grant.table in ('*', table):
                set.update(result, grant.privileges)

        if 'ALL PRIVILEGES' in result:
            return {'ALL PRIVILEGES'}

        if len(result) > 1:
            result.discard('USAGE')

        return result


def main():
    grants = MySQLGrant(user_engine)
    # pprint(grants._grants)

    print()
    print('Grants on test.*', grants.check_permissions('test'), sep='\t')
    print('Grants on test.test_table', grants.check_permissions('test', 'test_table'), sep='\t')
    print('Grants on test2.*', grants.check_permissions('test2'), sep='\t')
    print('Grants on test2.test_table', grants.check_permissions('test2', 'test_table'), sep='\t')


if __name__ == "__main__":
    main()
