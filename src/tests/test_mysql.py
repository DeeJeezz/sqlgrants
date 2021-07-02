import mock

from sqlgrants.mysql import MySQL, GrantType
from sqlgrants.mysql.grants import GrantLevel, Grants


def test_mysql_init():
    mysql = MySQL('username', 'password')
    url: str = mysql.engine.url.render_as_string(hide_password=False)
    assert url == 'mysql+mysqlconnector://username:password@127.0.0.1:3306/information_schema'


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
        ('GRANT USAGE ON *.* TO `user`@`%`',),
        ('GRANT SELECT ON `tests`.* TO `user`@`%`',)
    ]
    result = dict()
    result[GrantLevel.TABLE] = []
    result[GrantLevel.SCHEMA] = [Grants(privileges=['SELECT'], schema='tests', table='*')]
    result[GrantLevel.GLOBAL] = [Grants(privileges=['USAGE'], schema='*', table='*')]

    mysql = MySQL('admin', 'password')
    assert mysql._process_grant_list(data) == result

