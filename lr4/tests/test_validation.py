from app.users import validate_user_data
import pytest
from conftest import test_data
from app.auth import User

@pytest.mark.parametrize('input_data, expected', test_data())
def test_validate_user_data(input_data, expected):
    assert validate_user_data(input_data) == expected

@pytest.mark.parametrize('input_data, expected', test_data())
def test_validate_create(logged_in_client, captured_templates, input_data, expected, user_repository):
    with captured_templates as templates:
        new_user_data = {}
        new_user_data['login'] = input_data['login']
        new_user_data['password'] = input_data['password']
        new_user_data['first_name'] = input_data['first_name']
        new_user_data['last_name'] = input_data['last_name']
        new_user_data['middle_name'] = ''
        new_user_data['role_id'] = 1

        response = logged_in_client.post('/users/new', follow_redirects=True, data=new_user_data)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        if expected == {}:
            assert template.name == 'users/index.html'
            
            assert 'Пользователь создан.' in response.text

            assert new_user_data['login'] in response.text

            user_repository.delete(
                user_repository.get_with_login_password(new_user_data['login'], 
                                                             new_user_data['password']).id)
        else:
            assert template.name == 'users/new.html'

            for key in expected.keys():
                assert expected[key] in response.text

def test_validate_create_not_unique_login(app, existing_user, captured_templates):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.login)
            with app.test_client(user=user) as logged_in_client:
                new_user_data = {}
                new_user_data['login'] = existing_user.login
                new_user_data['password'] = 'Qwerty123'
                new_user_data['first_name'] = existing_user.first_name
                new_user_data['last_name'] = existing_user.last_name
                new_user_data['role_id'] = existing_user.role_id

                response = logged_in_client.post('/users/new', follow_redirects=True, data=new_user_data)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]
                
                assert template.name == 'users/new.html'
                    
                assert 'Ошибка при создании записи.' in response.text


@pytest.mark.parametrize('input_data, expected', test_data())
def test_validate_change_password_new_password(app, existing_user, captured_templates, input_data, expected, user_repository):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.login)
            with app.test_client(user=user) as logged_in_client:
                update_password = {}
                update_password['old_password'] = existing_user.password
                update_password['new_password'] = input_data['password']
                update_password['confirm_new_password'] = input_data['password']

                user_before_change = user_repository.get_with_id(existing_user.id)
                
                response = logged_in_client.post('/users/change_password', follow_redirects=True, data=update_password)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]

                if 'password' not in expected:
                    assert template.name == 'users/index.html'

                    assert 'Пароль изменён.' in response.text
                    
                    user_after_change = user_repository.get_with_id(existing_user.id)
                    assert user_before_change.password_hash != user_after_change.password_hash
                else:
                    assert template.name == 'users/password.html'

                    assert expected['password'] in response.text                   

def test_change_passwords_oldpass_incorrect(app, existing_user, captured_templates):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.login)
            with app.test_client(user=user) as logged_in_client:
                update_password = {}
                update_password['old_password'] = f"{existing_user.password}+"
                update_password['new_password'] = 'Qwerty1'
                update_password['confirm_new_password'] = 'Qwerty1'
                
                response = logged_in_client.post('/users/change_password', follow_redirects=True, data=update_password)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]

                assert template.name == 'users/password.html'
                assert 'Неверный текущий пароль.' in response.text 

def test_change_passwords_newpass_not_confirmed(app, existing_user, captured_templates):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.login)
            with app.test_client(user=user) as logged_in_client:
                update_password = {}
                update_password['old_password'] = f"{existing_user.password}+"
                update_password['new_password'] = 'Qwerty1'
                update_password['confirm_new_password'] = '1'
                
                response = logged_in_client.post('/users/change_password', follow_redirects=True, data=update_password)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]

                assert template.name == 'users/password.html'
                assert 'Подтвердите новый пароль.' in response.text 

def test_validate_edit_fail(logged_in_client, captured_templates):
    with captured_templates as templates:
        edit_user_info = {}
        edit_user_info['first_name'] = ''
        edit_user_info['second_name'] = ''
        edit_user_info['middle_name'] = 'Middle-name'
        edit_user_info['role_id'] = 1

        response = logged_in_client.post('/users/1/edit', follow_redirects=True, data=edit_user_info)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/edit.html'

        assert 'Поле не может быть пустым' in response.text

def test_validate_edit_success(logged_in_client, captured_templates):
    with captured_templates as templates:
        edit_user_info = {}
        edit_user_info['first_name'] = 'Amir'
        edit_user_info['last_name'] = 'Kulibabaev'
        edit_user_info['middle_name'] = 'Middle-name'
        edit_user_info['role_id'] = 1

        response = logged_in_client.post('/users/1/edit', follow_redirects=True, data=edit_user_info)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Запись изменена' in response.text
