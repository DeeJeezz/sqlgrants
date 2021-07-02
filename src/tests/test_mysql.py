import mock

from sqlgrants.mysql import MySQL


@mock.patch("sqlgrants.mysql.MySQL")
def test_mysql_init(mock_db):
    mysql = MySQL('username', 'password')
    url: str = mysql.engine.url.render_as_string(hide_password=False)
    assert url == 'mysql+mysqlconnector://username:password@127.0.0.1:3306/information_schema'
