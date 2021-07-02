[![](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://www.travis-ci.com/painassasin/sqlgrants.svg?branch=main)](https://www.travis-ci.com/painassasin/sqlgrants)
[![codecov](https://codecov.io/gh/painassasin/sqlgrants/branch/main/graph/badge.svg?token=8SH0DBNPTX)](https://codecov.io/gh/painassasin/sqlgrants)

## SQL Grants library

Supported databases:
- MySQL

## Examples of Usage

### Installation
```bash
python -m pip install python-sqlgrants
```

### Set and revoke grants
```python
from sqlgrants.mysql import MySQL, GrantType

mysql = MySQL('root', 'secret')

grant_types = {GrantType.SELECT, GrantType.INSERT}

# Revoke grants
mysql.revoke({GrantType.ALL}, username='username', schema='mysql')
assert mysql.show_grants(username='username', schema='mysql') == {GrantType.USAGE}

# Set grants
grants_set = {GrantType.SELECT, GrantType.INSERT}
mysql.grant({GrantType.SELECT, GrantType.INSERT}, username='username', schema='mysql')
assert mysql.show_grants(username='username', schema='mysql') == grants_set
```

## Show grants on tables and schemas 
```python
from pprint import pprint

from sqlgrants.mysql import MySQL, GrantType


mysql = MySQL('root', 'secret')
grants = mysql.tables_grants('user', '%', 'tests')
pprint(grants)

# {'tests': {'test_table_1': {SELECT, INSERT, UPDATE},
#            'test_table_2': {SELECT, INSERT},
#            'test_table_3': {SELECT, INSERT}}}
```