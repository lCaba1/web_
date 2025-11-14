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

def test_navbar_links_authorized(client_logged_as_user, captured_templates, example_users):
    with captured_templates as templates:
        response = client_logged_as_user.get('/')
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
        assert 'Просмотр' not in response.text

def test_index_authorized_as_user(client_logged_as_user, captured_templates, example_users):
    with captured_templates as templates:
        response = client_logged_as_user.get('/')

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Редактирование' in response.text
        assert 'Просмотр' in response.text

        assert 'Создание пользователя' not in response.text
        pattern = re.escape('data-user-id="') + r'\d+' + re.escape('">Удаление</button>')
        assert re.search(pattern, response.text) == None

def test_index_authorized_as_admin(client_logged_as_admin, captured_templates, example_users):
    with captured_templates as templates:
        response = client_logged_as_admin.get('/')

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Редактирование' in response.text
        assert 'Просмотр' in response.text
        assert 'Создание пользователя' in response.text

        pattern = re.escape('data-user-id="') + r'\d+' + re.escape('">Удаление</button>')
        assert re.search(pattern, response.text) != None

def test_delete_unauthorized(client, captured_templates, existing_user):
    with captured_templates as templates:
        response = client.post(f'/users/{existing_user.id}/delete', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_delete_authorized(client_logged_as_admin, captured_templates, user_repository, existing_admin):
    with captured_templates as templates:
        # Проверяем, что пользователь в БД существует
        assert user_repository.get_all() != []

        response = client_logged_as_admin.post(f'/users/1/delete', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Пользователь удален.' in response.text

        # Проверяем, что пользователя после удаления в БД больше нет
        assert user_repository.get_all() == []

def test_view_unexisted_user(client_logged_as_admin, captured_templates, example_users):
    with captured_templates as templates:
        response = client_logged_as_admin.get(f'/users/{len(example_users) + 1}', follow_redirects=True)

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
            user=User(existing_user.id, existing_user.login, existing_user.role_id)
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

