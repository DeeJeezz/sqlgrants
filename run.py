from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
import re
import enum
from dotenv import load_dotenv, find_dotenv
import os
from grants.utils import get_engine

load_dotenv(find_dotenv('.env', raise_error_if_not_found=True))
root_engine = get_engine('root', os.getenv('DB_PASS'))
user_engine = get_engine(os.getenv('DB_USER'), os.getenv('DB_PASS'))


# Еще надо обработать revoke
RE_GRANT = re.compile(r'GRANT (.*) ON (.*)\.(.*) TO (.*)@\'(.*)\'')


class GrantLevel(enum.Enum):
    GLOBAL = 0
    SCHEMA = 1
    TABLE = 2


class MySQLGrant:
    def __init__(self, engine: Engine, username: str = ''):
        self._engine = engine
        self._username = username or engine.url.username
        self._grants = dict.fromkeys(GrantLevel.__members__)
        self._update_grants()

    def _update_grants(self):
        try:
            with Session(self._engine) as session:
                query = session.execute(f'SHOW GRANTS FOR {self._username}')
                result = query.all()
        except Exception as e:
            raise e

        for grant in result:
            match = RE_GRANT.match(grant[0])
            if match:
                privileges = [p.strip() for p in match.group(1).split(',')]
                schema = match.group(2).strip('`')
                table = match.group(3).strip('`')

                if table != '*':
                    level = GrantLevel.TABLE
                elif schema != '*':
                    level = GrantLevel.SCHEMA
                else:
                    level = GrantLevel.GLOBAL

                print('Privileges:', privileges)
                print('Schema:', schema)
                print('Table:', table)
                print('Level:', level)

            print()


def main():
    print('='*10, 'ROOT', '='*10)
    MySQLGrant(root_engine)

    print('='*10, 'USER', '='*10)
    MySQLGrant(user_engine)


if __name__ == "__main__":
    main()
