from lab5.users import validate_user_data
import pytest
from conftest import test_data
from lab5.auth import User

@pytest.mark.parametrize('input_data, expected', test_data())
def test_validate_user_data(input_data, expected):
    assert validate_user_data(input_data) == expected

@pytest.mark.parametrize('input_data, expected', test_data())
def test_validate_create(client_logged_as_admin, captured_templates, input_data, expected, user_repository, existing_admin):
    with captured_templates as templates:
        new_user_data = {}
        new_user_data['username'] = input_data['username']
        new_user_data['password'] = input_data['password']
        new_user_data['first_name'] = input_data['first_name']
        new_user_data['last_name'] = input_data['last_name']
        new_user_data['middle_name'] = ''
        new_user_data['role_id'] = existing_admin.role_id

        response = client_logged_as_admin.post('/users/new', follow_redirects=True, data=new_user_data)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        if expected == {}:
            assert template.name == 'users/index.html'
            
            assert 'Учётная запись успешно создана.' in response.text

            assert new_user_data['username'] in response.text

            user_repository.delete(
                user_repository.get_by_username_and_password(new_user_data['username'], 
                                                             new_user_data['password']).id)
        else:
            assert template.name == 'users/new.html'

            for key in expected.keys():
                assert expected[key] in response.text

def test_validate_create_not_unique_username(app, existing_admin, captured_templates):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_admin.id, existing_admin.username, existing_admin.role_id)
            with app.test_client(user=user) as logged_in_client:
                new_user_data = {}
                new_user_data['username'] = existing_admin.username
                new_user_data['password'] = 'Qwerty123'
                new_user_data['first_name'] = existing_admin.first_name
                new_user_data['last_name'] = existing_admin.last_name
                new_user_data['role_id'] = existing_admin.role_id

                response = logged_in_client.post('/users/new', follow_redirects=True, data=new_user_data)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]
                
                assert template.name == 'users/new.html'
                    
                assert 'Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены.' in response.text


@pytest.mark.parametrize('input_data, expected', test_data())
def test_validate_change_password_new_password(app, existing_user, captured_templates, input_data, expected, user_repository):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.username, existing_user.role_id)
            with app.test_client(user=user) as logged_in_client:
                update_password = {}
                update_password['old_password'] = existing_user.password
                update_password['new_password'] = input_data['password']
                update_password['confirm_new_password'] = input_data['password']

                user_before_change = user_repository.get_by_id(existing_user.id)
                
                response = logged_in_client.post('/users/change_password', follow_redirects=True, data=update_password)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]

                if 'password' not in expected:
                    assert template.name == 'users/index.html'

                    assert 'Пароль успешно изменён!' in response.text
                    
                    user_after_change = user_repository.get_by_id(existing_user.id)
                    assert user_before_change.password_hash != user_after_change.password_hash
                else:
                    assert template.name == 'users/password.html'

                    assert expected['password'] in response.text                   

def test_change_passwords_oldpass_incorrect(app, existing_user, captured_templates):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.username, existing_user.role_id)
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
                assert 'Старый пароль указан неверно' in response.text 

def test_change_passwords_newpass_not_confirmed(app, existing_user, captured_templates):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.username, existing_user.role_id)
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
                assert 'Пароли не совпадают' in response.text 

def test_validate_edit_fail(client_logged_as_admin, captured_templates, existing_admin):
    with captured_templates as templates:
        edit_user_info = {}
        edit_user_info['first_name'] = ''
        edit_user_info['second_name'] = ''
        edit_user_info['middle_name'] = 'Middle-name'
        edit_user_info['role_id'] = 1

        response = client_logged_as_admin.post('/users/1/edit', follow_redirects=True, data=edit_user_info)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/edit.html'

        assert 'Поле не может быть пустым' in response.text

def test_validate_edit_success(client_logged_as_admin, captured_templates, existing_admin):
    with captured_templates as templates:
        edit_user_info = {}
        edit_user_info['first_name'] = 'Amir'
        edit_user_info['last_name'] = 'Kulibabaev'
        edit_user_info['middle_name'] = 'Middle-name'
        edit_user_info['role_id'] = existing_admin.role_id

        response = client_logged_as_admin.post('/users/1/edit', follow_redirects=True, data=edit_user_info)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'
        assert 'Учётная запись успешно изменена' in response.text
