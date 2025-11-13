import os
from functools import reduce
from collections import namedtuple
import logging
import pytest
import mysql.connector
from app import create_app
from app.dbconnector import DBConnector
from app.repositories import RoleRepository
from app.repositories import UserRepository

from flask_login import FlaskLoginClient
from contextlib import contextmanager
from flask import Flask, template_rendered
from app.auth import User

TEST_DB_CONFIG = {
    'MYSQL_HOST': '127.0.0.1',
    'MYSQL_PORT': '3306',
    'MYSQL_USER': 'lab4_user',
    'MYSQL_PASSWORD': 'lab4_password',
    'MYSQL_DATABASE': 'lab4_test_db'
}


def get_connection(app):
    return mysql.connector.connect(
        user = app.config['MYSQL_USER'],
        password = app.config['MYSQL_PASSWORD'],
        host = app.config['MYSQL_HOST']
    )

def setup_db(app):
    logging.getLogger().info("Create db...")

    test_db_name = app.config['MYSQL_DATABASE']
    create_db_query = f"""DROP DATABASE IF EXISTS {test_db_name}; 
                          CREATE DATABASE {test_db_name}; 
                          USE {test_db_name};"""

    with app.open_resource('../tests/test_db.sql') as f:
        connection = get_connection(app)

        sql_script = f.read().decode('utf8')
        schema_query = [q.strip() for q in sql_script.split(';') if q.strip()]

        create_db_queries = [q.strip() for q in create_db_query.split(';') if q.strip()]
        # queries = '\n'.join([create_db_query, schema_query])

        with connection.cursor() as cursor:
            for query in create_db_queries:
                if query:
                    cursor.execute(query)
            for query in schema_query:
                if query:
                    cursor.execute(query)
        connection.commit()
        connection.close()

def teardown_db(app):
    logging.getLogger().info("Drop db...")
    test_db_name = app.config['MYSQL_DATABASE']
    connection = get_connection(app)
    with connection.cursor() as cursor:
        cursor.execute(f'DROP DATABASE IF EXISTS {test_db_name}')
    connection.close()

###############################

@pytest.fixture(scope='session')
def app():
    app = create_app(TEST_DB_CONFIG)
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })
    app.test_client_class = FlaskLoginClient
    yield app

@pytest.fixture
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        print(**extra)
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture()
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client

@pytest.fixture
def logged_in_client(app, existing_user):
    with app.app_context():
        user=User(existing_user.id, existing_user.login)
        with app.test_client(user=user) as logged_in_client:
            yield logged_in_client

#################################

@pytest.fixture(scope='session')
def db_connector(app):
    setup_db(app)
    with app.app_context():
        connector = DBConnector(app)
        yield connector
        connector.disconnect()
    teardown_db(app)

@pytest.fixture
def role_repository(db_connector):
    return RoleRepository(db_connector)

@pytest.fixture
def existing_role(db_connector):
    data = (1, 'admin')
    row_class = namedtuple('Row', ['id', 'name'])
    role = row_class(*data)

    connection = db_connector.connect()
    with connection.cursor() as cursor:
        query = 'INSERT INTO roles(id, name) VALUES (%s, %s);'
        cursor.execute(query, data)
        connection.commit()

    yield role

    with connection.cursor() as cursor:
        query = 'DELETE FROM roles WHERE id=%s'
        cursor.execute(query, (role.id,))
        connection.commit()

@pytest.fixture
def nonexisting_role_id():
    return 1

@pytest.fixture
def example_roles(db_connector):
    data = [(1, 'admin'), (2, 'test')]
    row_class = namedtuple('Row', ['id', 'name'])
    roles = [row_class(*row_data) for row_data in data]

    connection = db_connector.connect()
    with connection.cursor() as cursor:
        placeholders = ', '.join(['(%s, %s)' for _ in range(len(data))])
        query = f'INSERT INTO roles(id, name) VALUES {placeholders};'
        cursor.execute(query, reduce(lambda seq, x: seq + list(x), data, []))
        connection.commit()

    yield roles

    with connection.cursor() as cursor:
        role_ids = ', '.join([str(role.id) for role in roles])
        query = f'DELETE FROM roles WHERE id IN ({role_ids});'
        cursor.execute(query)
        connection.commit()

@pytest.fixture
def user_repository(db_connector):
    return UserRepository(db_connector)

@pytest.fixture
def existing_user(db_connector, existing_role):
    user_data = (1, 'admin', 'qwerty', 'Студент', 'Студент', int(existing_role.id))
    row_class = namedtuple('Row', ['id', 'login', 'password', 'first_name', 'last_name', 'role_id'])
    user = row_class(*user_data)

    connection = db_connector.connect()
    with connection.cursor(named_tuple=True) as cursor:
        query = (
            "INSERT INTO users (id, login, password_hash, first_name, last_name, role_id) VALUES "
            "(%s, %s, SHA2(%s, 256), %s, %s, %s);"
        )
        cursor.execute(query, user_data)
        connection.commit()

    yield user

    with connection.cursor() as cursor:
        query = 'DELETE FROM users WHERE id=%s'
        cursor.execute(query, (user.id,))
        connection.commit()

@pytest.fixture
def nonexisting_user():
    user_data = (1, 'admin', 'qwerty', 'Студент', 'Студент', '1')
    row_class = namedtuple('Row', ['id', 'login', 'password', 'first_name', 'last_name', 'role_id'])
    user = row_class(*user_data)

    return user

@pytest.fixture
def example_users(db_connector, existing_role):
    data = [
        (1, 'admin', 'qwerty', 'Студент', 'Студент', existing_role.id), 
        (2, 'test', 'qwerty', 'Тест', 'Тест', existing_role.id)
    ]
    row_class = namedtuple('Row', ['id', 'login', 'password', 'first_name', 'last_name', 'role_id'])
    users = [row_class(*row_data) for row_data in data]

    connection = db_connector.connect()
    with connection.cursor() as cursor:
        placeholders = ', '.join(['(%s, %s, SHA2(%s, 256), %s, %s, %s)' for _ in range(len(data))])
        query = f"INSERT INTO users(id, login, password_hash, first_name, last_name, role_id) VALUES {placeholders};"
        cursor.execute(query, reduce(lambda seq, x: seq + list(x), data, []))
        connection.commit()

    yield users

    with connection.cursor() as cursor:
        user_ids = ', '.join([str(user.id) for user in users])
        query = f'DELETE FROM users WHERE id IN ({user_ids});'
        cursor.execute(query)
        connection.commit()


def test_data():
    return [
        (
            {'login': 'test1',
             'password': 'Test1234',
             'first_name': 'Test',
             'last_name': 'Test'}, {}
        ),
        (
            {'login': '',
             'password': '',
             'first_name': '',
             'last_name': ''}, 
            {'login': 'Поле не может быть пустым',
             'password': 'Поле не может быть пустым',
             'first_name': 'Поле не может быть пустым',
             'last_name': 'Поле не может быть пустым'}
        ),
        (
            {'login': 'a',
             'password': 'Test1234',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'login': 'Логин должен содержать не менее 5 символов'}
        ),
        (
            {'login': 'тест1',
             'password': 'Test1234',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'login': 'Логин должен содержать только латинские буквы и цифры'}
        ),
        (
            {'login': 'Test1',
             'password': 'Test123',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'password': 'Пароль должен содержать не менее 8 символов'}
        ),
        (
            {'login': 'Test1',
             'password': 'Qa2345678910Qa2345678910Qa2345678910Qa2345678910Qa23456789'
            '10Qa2345678910Qa2345678910Qa2345678910Qa2345678910Qa2345678910Qa2345678910Qa2345678910Qa2345678910',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'password': 'Пароль должен содержать не более 128 символов'}
        ),
        (
            {'login': 'Test1',
             'password': 'a1234567',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'password': 'Пароль должен содержать хотя бы одну заглавную букву'}
        ),
        (
            {'login': 'Test1',
             'password': 'Q12345678',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'password': 'Пароль должен содержать хотя бы одну строчную букву'}
        ),
        (
            {'login': 'Test1',
             'password': 'Qazwsxedc',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'password': 'Пароль должен содержать хотя бы одну цифру'}
        ),
        (
            {'login': 'Test1',
             'password': 'Qazwsxe132c☻♠○◘♣♥•♦☺♫◄↕☺►♪',
             'first_name': 'Test',
             'last_name': 'Test'},
            {'password': 'Пароль содержит недопустимые символы'}
        ),
    ]