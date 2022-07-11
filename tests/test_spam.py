import mysql.connector
from mysql.connector import connection, errorcode

import pytest

from MySQLHandler import MySQLHandler

USER_TABLE_SQL = '''
    drop table if exists users;
    create table users
    (
        id             bigint auto_increment,
        user_id        bigint           not null,
        first_name     varchar(255)     null,
        last_name      varchar(255)     null,
        username       varchar(255)     null,
        phone          varchar(100)     null,
        kicked         bit default b'0' null,
        root           bit default b'0' not null,
        bash_execution bit default b'0' not null,
        constraint id
            unique (id),
        constraint user_id
            unique (user_id)
    );

    alter table users
        add primary key (id);
    '''

BOT_GROUPS_SQL = '''
    drop table if exists bot_groups;

    create table bot_groups
    (
        id        bigint auto_increment,
        group_name varchar(255) null,
        group_id  bigint       not null,
        constraint chat_name
            unique (group_name),
        constraint group_id
            unique (group_id),
        constraint id
            unique (id)
    );

    alter table bot_groups
        add primary key (id);
'''


@pytest.fixture
def db_handler():
    config = {
        'user': 'root',
        'password': '8syqxe',
        'host': '127.0.0.1',
        'database': 'test_db',
        'raise_on_warnings': True
    }
    
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    db = MySQLHandler(config)
    # cursor.execute('DROP TABLE IF EXISTS users')
    # db.cursor.execute(
    #                   "create table users("
    #                   "id             SERIAL,"
    #                   "user_id        bigint           not null UNIQUE ,"
    #                   "first_name     varchar(255)     null,"
    #                   "last_name      varchar(255)     null,"
    #                   "username       varchar(255)     null,"
    #                   "phone          varchar(100)     null,"
    #                   "kicked         bit default 0 null,"
    #                   "root           bit default 0 not null,"
    #                   "bash_execution bit default 0 not null)")
    
    # db.cursor.execute("drop table if exists bot_groups;"
    #                   "create table bot_groups("
    #                   "id bigint auto_increment,"
    #                   "group_name varchar(255) null,"
    #                   "group_id  bigint not null,"
    #                   "constraint chat_name unique (group_name),"
    #                   "constraint group_id unique (group_id),"
    #                   "constraint id unique (id));"
    #                   "alter table bot_groups add primary key (id);", multi=True)
    

    cursor.execute('CREATE TABLE users (name VARCHAR(255), address VARCHAR(255))')
    
    yield db
    db.connector.close()


#
# @pytest.fixture
# def setup_db(db_handler):
#     db_handler.cursor.execute(USER_TABLE_SQL, multi=True)


# @pytest.mark.usefixtures('setup_db')
def test_add_new_user(db_handler):
    db_handler.save_user('12345', 'Harry', 'Potter', 'The_Boy_Who_Lived')
    assert db_handler.get_db_user_id('12345') == 1

# def test_get_all_users(db_handler):
#     all_users = db_handler.get_all_users()
#     print(all_users)
#     assert db_handler.get_all_users() == [(1, 12345, 'Harry', 'Potter', 'The_Boy_Who_Lived', None, 0, 0, 0)]
