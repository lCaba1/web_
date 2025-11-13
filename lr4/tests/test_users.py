import re
from app.auth import User

def test_navbar_links_unathorized(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Войти' in response.text
        assert 'Выйти' not in response.text
        assert 'Изменить пароль' not in response.text

def test_navbar_links_authorized(logged_in_client, captured_templates):
    with captured_templates as templates:
        response = logged_in_client.get('/')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Войти' not in response.text
        assert 'Выйти' in response.text
        assert 'Изменить пароль' in response.text

def test_index_unauthorized(client, captured_templates, example_users):
    with captured_templates as templates:
        response = client.get('/')

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Редактирование' not in response.text

        pattern = re.escape('data-user-id="') + r'\d+' + re.escape('">Удаление</button>')
        assert re.search(pattern, response.text) == None
        
        assert 'Создание пользователя' not in response.text
        assert 'Просмотр' in response.text

def test_index_authorized(logged_in_client, captured_templates):
    with captured_templates as templates:
        response = logged_in_client.get('/')

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Редактирование' in response.text
        
        pattern = re.escape('data-user-id="') + r'\d+' + re.escape('">Удаление</button>')
        assert re.search(pattern, response.text) != None

        assert 'Создание пользователя' in response.text
        assert 'Просмотр' in response.text

def test_edit_unauthorized(client, captured_templates, existing_user):
    with captured_templates as templates:
        response = client.get(f'/users/{existing_user.id}/edit', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_edit_authorized(captured_templates, logged_in_client, user_repository):
    with captured_templates as templates:
        response = logged_in_client.get(f'/users/1/edit', follow_redirects=True)
        
        assert response.status_code == 200
        
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/edit.html'
        
        # User до изменения
        user = user_repository.get_with_id('1')
        
        update_field = {}
        update_field['first_name'] = f"{user.first_name}_test"
        update_field['last_name'] = f"{user.last_name}_test"
        update_field['middle_name'] = f"{user.middle_name if user.middle_name else 'middle_name'}_test"
        update_field['role_id'] = user.role_id
        response = logged_in_client.post(f'/users/1/edit', follow_redirects=True, data=update_field)

        assert response.status_code == 200

        assert len(templates) == 2
        template = templates[1][0]
        assert template.name == 'users/index.html'

        assert 'Запись изменена' in response.text

        updated_user = user_repository.get_with_id(str(user.id))
        assert updated_user.role_id == user.role_id
        assert updated_user.first_name == f"{user.first_name}_test"
        assert updated_user.last_name == f'{user.last_name}_test' 
        assert updated_user.middle_name == f"{user.middle_name if user.middle_name else 'middle_name'}_test"

def test_delete_unauthorized(client, captured_templates, existing_user):
    with captured_templates as templates:
        response = client.post(f'/users/{existing_user.id}/delete', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_delete_authorized(logged_in_client, captured_templates, user_repository):
    with captured_templates as templates:
        # Проверяем, что пользователь в БД существует
        assert user_repository.get_all() != []

        response = logged_in_client.post(f'/users/1/delete', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Пользователь удален.' in response.text

        # Проверяем, что пользователя после удаления в БД больше нет
        assert user_repository.get_all() == []

def test_view(client, captured_templates, existing_user, existing_role):
    with captured_templates as templates:
        response = client.get(f'/users/{existing_user.id}', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/show.html'

        assert str(existing_user.id) in response.text
        assert existing_user.login in response.text
        assert existing_user.first_name in response.text
        assert existing_user.last_name in response.text
        assert existing_role.name in response.text

def test_view_unexisted_user(client, captured_templates, existing_user, existing_role):
    with captured_templates as templates:
        response = client.get(f'/users/{existing_user.id + 1}', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Нет пользователя с таким id.' in response.text

def test_create_unauthorized(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/users/new', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_create_authorized(logged_in_client, captured_templates, user_repository):
    with captured_templates as templates:
        response = logged_in_client.get('/users/new', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/new.html'

        # Сохранение информации о пользователях до создания нового пользователя
        users = user_repository.get_all()
        
        new_user_data = {}
        new_user_data['login'] = 'test1'
        new_user_data['password'] = 'Test_password1'
        new_user_data['first_name'] = 'test_first_name'
        new_user_data['middle_name'] = 'test_middle_name'
        new_user_data['last_name'] = 'test_last_name'
        new_user_data['role_id'] = '1'
        response = logged_in_client.post('/users/new', follow_redirects=True, data=new_user_data)

        assert response.status_code == 200

        assert len(templates) == 2
        template = templates[1][0]
        assert template.name == 'users/index.html'  
        
        # Новый пользователь появился на основной странице
        assert new_user_data['login'] in response.text

        # Сохранение информации о пользователях после создания нового пользователя
        new_users = user_repository.get_all()

        assert len(new_users) == len(users) + 1

        # assert new_user_data['id'] + 1 == new_users[1].id
        assert new_user_data['login'] == new_users[1].login
        assert new_user_data['first_name'] == new_users[1].first_name
        assert new_user_data['middle_name'] == new_users[1].middle_name
        assert new_user_data['last_name'] == new_users[1].last_name
        assert int(new_user_data['role_id']) == new_users[1].role_id

        # Удаляем нового пользователя
        user_repository.delete(new_users[1].id)

def test_change_password_unauthorized(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/users/change_password', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_change_password_authorized(captured_templates, user_repository, app, existing_user):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.login)
            with app.test_client(user=user) as logged_in_client:
                response = logged_in_client.get('/users/change_password', follow_redirects=True)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]
                assert template.name == 'users/password.html'

                user_before_change = user_repository.get_with_id(existing_user.id)

                change_password_form = {}
                change_password_form['old_password'] = existing_user.password
                change_password_form['new_password'] = 'Test1234'
                change_password_form['confirm_new_password'] = 'Test1234'
                response = logged_in_client.post('/users/change_password', follow_redirects=True, data=change_password_form)
                assert response.status_code == 200

                assert len(templates) == 2
                template = templates[1][0]
                assert template.name == 'users/index.html'

                user_after_change = user_repository.get_with_id(existing_user.id)

                assert user_before_change.password_hash != user_after_change.password_hash

