from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


def get_engine(username: str, password: str, host: str = '127.0.0.1',
               port: int = 3306, schema: str = '') -> Engine:
    dialect = 'mysql'
    driver = 'mysqlconnector'
    schema = schema or 'information_schema'
    url = f'{dialect}+{driver}://{username}:{password}@{host}:{port}/{schema}'
    return create_engine(url)
