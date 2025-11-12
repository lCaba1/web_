import pytest
from flask import Flask, template_rendered
from flask_login import FlaskLoginClient
from contextlib import contextmanager
from app import app as application, User, get_user

application.test_client_class = FlaskLoginClient

@pytest.fixture
def app():
    application.config['TESTING'] = True
    application.config['WTF_CSRF_ENABLED'] = False 
    return application

@pytest.fixture
def client():
    with application.test_client() as client:
        yield client

@pytest.fixture
def logged_in_client():
    user=User('1', 'user')
    with application.test_client(user=user) as logged_in_client:
        yield logged_in_client

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

@pytest.fixture
def login_data():
    return [
        {
            'username': 'user',
            'password': 'qwerty',
            'remember_me': 'on'
        },
        {
            'username': 'user',
            'password': 'any_password'
        },
        {
            'username': 'user',
            'password': 'qwerty'
        }
    ]