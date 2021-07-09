import re
from typing import Set, Dict, List, Optional

from sqlgrants.base import BaseDatabase
from sqlgrants.exceptions import NotFoundError
from .grants import GrantLevel, Grants, GrantType


class MySQL(BaseDatabase):
    RE_GRANT: re.Pattern = re.compile(r'GRANT (?P<privileges>.*) ON (?P<schema>\S*)\.(?P<table>\S*)')

    def __init__(self, login: str, password: str, host: str = '127.0.0.1', port: int = 3306):
        super().__init__('mysql', 'mysqlconnector', 'information_schema')
        self._login: str = login
        self.engine: str = self._create_engine_url(login, password, host, port)

    def _process_grant_list(self, grant_list: Optional[list]) -> Dict[GrantLevel, List[Grants]]:
        grants: Dict[GrantLevel, list] = {key: [] for key in GrantLevel}
        for grant in grant_list:
            match: Optional[re.Match] = self.RE_GRANT.match(grant[0])
            if match:
                privileges: List[str] = [p.strip() for p in match.group('privileges').split(',')]
                schema: str = match.group('schema').strip('`')
                table: str = match.group('table').strip('`')

                if table != '*':
                    level: GrantLevel = GrantLevel.TABLE
                elif schema != '*':
                    level: GrantLevel = GrantLevel.SCHEMA
                else:
                    level: GrantLevel = GrantLevel.GLOBAL

                grants[level].append(Grants(privileges, schema, table))
        return grants

    def _show_grants(self, username: str, host: str) -> Dict[GrantLevel, List[Grants]]:
        data: Optional[list] = self.execute(f'SHOW GRANTS FOR \'{username}\'@\'{host}\'')
        return self._process_grant_list(data)

    def show_grants(
            self,
            *,
            username: str = '',
            host: str = '%',
            schema: str = '*',
            table: str = '*',
    ) -> Set[GrantType]:
        grants: Dict[GrantLevel, List[Grants]] = self._show_grants(username or self._login, host)
        result: set = set()

        for grant_level in GrantLevel:
            for grant in grants[grant_level]:
                if grant.schema in ('*', schema) and grant.table in ('*', table):
                    set.update(result, [GrantType(p) for p in grant.privileges if p in GrantType.values()])

        if GrantType.ALL in result:
            return {GrantType.ALL}

        if len(result) > 1:
            result.discard(GrantType.USAGE)

        return result

    def grant(
            self,
            grants: Set[GrantType],
            *,
            username: str = '',
            host: str = '%',
            schema: str = '*',
            table: str = '*',
    ) -> None:
        grant_types: str = ', '.join({grant_type.value for grant_type in grants})
        sql: str = f'GRANT {grant_types} ON {schema}.{table} TO \'{username or self._login}\'@\'{host}\''
        self.execute(sql)

    def revoke(
            self,
            grants: Set[GrantType],
            *,
            username: str = '',
            host: str = '%',
            schema: str = '*',
            table: str = '*',
    ) -> None:
        grant_types: str = ', '.join({grant_type.value for grant_type in grants})
        sql: str = f'REVOKE {grant_types} ON {schema}.{table} FROM \'{username or self._login}\'@\'{host}\''
        self.execute(sql)

    def _schemas_dict(self, schema: str = '') -> Dict[str, dict]:
        if schema:
            return {_schema.name: {} for _schema in self.schemas if _schema.name == schema}
        else:
            return {_schema.name: {} for _schema in self.schemas}

    def tables_grants(self, username: str, host: str, schema: str = '', table: str = '') -> Dict[str, dict]:
        user: Dict[str, str] = {'username': username, 'host': host}
        result: Dict[str, dict] = self._schemas_dict(schema)
        if schema and not result:
            raise NotFoundError(f'schema \'{schema}\' not found')
        for _schema in self.schemas:
            if _schema.name in result:
                if not _schema.tables:
                    if table:
                        raise NotFoundError(f'table \'{table}\' not found')
                    grants: Set[GrantType] = self.show_grants(schema=_schema.name, **user)
                    result[_schema.name]['*'] = grants
                    continue
                for _table in _schema.tables:
                    if table and _table.name != table:
                        continue
                    grants: Set[GrantType] = self.show_grants(schema=_table.schema, table=_table.name, **user)
                    result[_table.schema][_table.name] = grants
        return result
