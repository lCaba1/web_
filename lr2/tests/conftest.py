from datetime import datetime
import pytest
from flask import template_rendered
from contextlib import contextmanager
from app import app as application

@pytest.fixture
def app():
    return application

@pytest.fixture
def client(app):
    return app.test_client()

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
def test_data():
    return {
        'test_url_params': {
            'param_1': '123456',
            'param_2': 'pytest'
        },
        'test_request_headers': {
            'header_1': '123456',
            'header_2': 'pytest'
        },
        'test_cookie': {
            'test_cookie': 'This_is_test_cookie!'
        },
        'test_form_params': {
            'test_form_data': 'test_form_params'
        },
        'test_error_handling_form': {
            'input': {
                'phone_number': [
                    '+7 (123) 456-78-90',
                    '8(123)4567890',
                    '123.456.78.90',
                    '123456',
                    '812345678901',
                    '12345678901',
                    '+7 (123) 456-78-90O'
                ]
            },
            'output': {
                '+7 (123) 456-78-90': '8-123-456-78-90',
                '8(123)4567890': '8-123-456-78-90',
                '123.456.78.90': '8-123-456-78-90',
                '123456': 'Недопустимый ввод. Неверное количество цифр.',
                '812345678901': 'Недопустимый ввод. Неверное количество цифр.',
                '12345678901': 'Недопустимый ввод. Неверное количество цифр.',
                '+7 (123) 456-78-90O': 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
            }
        }
    }