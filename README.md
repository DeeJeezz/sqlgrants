[![codecov](https://codecov.io/gh/painassasin/sqlgrants/branch/main/graph/badge.svg?token=8SH0DBNPTX)](https://codecov.io/gh/painassasin/sqlgrants)

# SQL Grants library
## Install
```bash
pip install python-sqlgrants
```
## Usage
```python
from sqlgrants.mysql import MySQL, GrantType

login: str = 'user'
password: str = 'password'
schema: str = 'test'

mysql = MySQL(login, password)
grant_types = {GrantType.SELECT, GrantType.INSERT}

mysql.revoke({GrantType.ALL}, schema=schema)
assert mysql.show_grants(schema=schema) == {GrantType.USAGE}

mysql.grant(grant_types, schema=schema)
assert mysql.show_grants(schema=schema) == grant_types
```