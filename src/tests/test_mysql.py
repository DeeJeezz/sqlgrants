import mock
from sqlgrants.base import Schema, Table
from sqlgrants.mysql import GrantType, MySQL
from sqlgrants.mysql.grants import GrantLevel, Grants


def test_init():
    mysql = MySQL('username', 'password')
    url: str = mysql.engine.url.render_as_string(hide_password=False)
    assert url == 'mysql+mysqlconnector://username:password@127.0.0.1:3306/information_schema'


def test_execute():
    mysql = MySQL('username', 'password')
    mysql.engine = 'sqlite:///:memory:'
    response = mysql.execute('SELECT date("now");')
    assert isinstance(response, list)


@mock.patch.object(MySQL, 'execute')
def test_schemas_property(mock_execute):
    mock_execute.return_value = [('information_schema',)]
    tmp = MySQL('username', 'password')
    assert isinstance(tmp.schemas, list)
    for schema in tmp.schemas:
        assert isinstance(schema, Schema)
    schema = tmp.schemas[0]
    assert schema.name == 'information_schema'
    mock_execute.return_value = [('table_1',), ('table_2',)]
    assert isinstance(schema.tables, list)
    for table in schema.tables:
        assert isinstance(table, Table)


@mock.patch.object(MySQL, 'execute')
def test_schemas_dict(mock_execute):
    mock_execute.return_value = [('information_schema',), ('mysql',)]
    tmp = MySQL('username', 'password')

    schema_dict = tmp._schemas_dict()
    assert isinstance(schema_dict, dict)
    assert set(schema_dict.keys()) == {'information_schema', 'mysql'}

    schema_dict = tmp._schemas_dict('mysql')
    assert isinstance(schema_dict, dict)
    assert set(schema_dict.keys()) == {'mysql'}


@mock.patch.object(MySQL, 'execute')
def test_grants_showing(mock_execute):
    mysql = MySQL('username', 'password')

    mysql.show_grants()
    mock_execute.assert_called_with('SHOW GRANTS FOR \'username\'@\'%\'')

    mysql.show_grants(username='root')
    mock_execute.assert_called_with('SHOW GRANTS FOR \'root\'@\'%\'')


@mock.patch.object(MySQL, 'execute')
def test_grant_and_revoke(mock_execute):
    mysql = MySQL('admin', 'password')

    mysql.grant({GrantType.SELECT})
    mock_execute.assert_called_with('GRANT SELECT ON *.* TO \'admin\'@\'%\'')

    mysql.revoke({GrantType.ALL}, username='username', schema='mysql')
    mock_execute.assert_called_with('REVOKE ALL PRIVILEGES ON mysql.* FROM \'username\'@\'%\'')


def test_process_grant_list():
    data = [
        ("GRANT USAGE ON *.* TO 'user'@'%' IDENTIFIED BY PASSWORD '*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9'",),
        ("GRANT ALL PRIVILEGES ON `grants`.* TO 'user'@'%'",),
        ("GRANT SELECT ON `test_schema`.* TO 'user'@'%'",),
        ("GRANT INSERT ON `test_schema`.`test_table` TO 'user'@'%'",),
    ]
    result = dict()
    result[GrantLevel.TABLE] = [
        Grants(privileges=['INSERT'], schema='test_schema', table='test_table'),
    ]
    result[GrantLevel.SCHEMA] = [
        Grants(privileges=['ALL PRIVILEGES'], schema='grants', table='*'),
        Grants(privileges=['SELECT'], schema='test_schema', table='*'),
    ]
    result[GrantLevel.GLOBAL] = [
        Grants(privileges=['USAGE'], schema='*', table='*')
    ]

    mysql = MySQL('user', 'password')
    assert mysql._process_grant_list(data) == result


@mock.patch.object(MySQL, '_show_grants')
def test_show_grants(mock_show_grants):
    data = [
        ("GRANT USAGE ON *.* TO 'user'@'%' IDENTIFIED BY PASSWORD '*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9'",),
        ("GRANT ALL PRIVILEGES ON `grants`.* TO 'user'@'%'",),
        ("GRANT SELECT, INSERT ON `test_schema`.* TO 'user'@'%'",),
    ]
    tmp = MySQL('user', 'password')
    mock_show_grants.return_value = tmp._process_grant_list(data)
    assert tmp.show_grants() == {GrantType.USAGE}
    assert tmp.show_grants(schema='grants') == {GrantType.ALL}
    assert tmp.show_grants(schema='test_schema') == {GrantType.SELECT, GrantType.INSERT}
