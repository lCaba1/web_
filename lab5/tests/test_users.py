import re
from lab5.auth import User

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
        assert 'Выход' in response.text
        assert 'Изменить пароль' in response.text

def test_index_unauthorized(client, captured_templates, example_users):
    with captured_templates as templates:
        response = client.get('/')

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Редактировать' not in response.text

        pattern = re.escape('data-user-id="') + r'\d+' + re.escape('">Удалить</button>')
        assert re.search(pattern, response.text) == None
        
        assert 'Добавить пользователя' not in response.text
        assert 'Просмотр' not in response.text

def test_index_authorized_as_user(client_logged_as_user, captured_templates, example_users):
    with captured_templates as templates:
        response = client_logged_as_user.get('/')

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Редактировать' in response.text
        assert 'Просмотр' in response.text

        assert 'Добавить пользователя' not in response.text
        pattern = re.escape('data-user-id="') + r'\d+' + re.escape('">Удалить</button>')
        assert re.search(pattern, response.text) == None

def test_index_authorized_as_admin(client_logged_as_admin, captured_templates, example_users):
    with captured_templates as templates:
        response = client_logged_as_admin.get('/')

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Редактировать' in response.text
        assert 'Просмотр' in response.text
        assert 'Добавить пользователя' in response.text

        pattern = re.escape('data-user-id="') + r'\d+' + re.escape('">Удалить</button>')
        assert re.search(pattern, response.text) != None

def test_delete_unauthorized(client, captured_templates, existing_user):
    with captured_templates as templates:
        response = client.post(f'/users/{existing_user.id}/delete', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/login.html'

def test_delete_authorized(client_logged_as_admin, captured_templates, user_repository, existing_admin):
    with captured_templates as templates:
        # Проверяем, что пользователь в БД существует
        assert user_repository.all() != []

        response = client_logged_as_admin.post(f'/users/1/delete', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Учётная запись успешно удалена' in response.text

        # Проверяем, что пользователя после удаления в БД больше нет
        assert user_repository.all() == []

def test_view_unexisted_user(client_logged_as_admin, captured_templates, example_users):
    with captured_templates as templates:
        response = client_logged_as_admin.get(f'/users/{len(example_users) + 1}', follow_redirects=True)

        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Пользователя нет в базе данных' in response.text

def test_create_unauthorized(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/users/new', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/login.html'

def test_change_password_unauthorized(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/users/change_password', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/login.html'

def test_change_password_authorized(captured_templates, user_repository, app, existing_user):
    with captured_templates as templates:
        with app.app_context():
            user=User(existing_user.id, existing_user.username, existing_user.role_id)
            with app.test_client(user=user) as logged_in_client:
                response = logged_in_client.get('/users/change_password', follow_redirects=True)
                assert response.status_code == 200

                assert len(templates) == 1
                template = templates[0][0]
                assert template.name == 'users/password.html'

                user_before_change = user_repository.get_by_id(existing_user.id)

                change_password_form = {}
                change_password_form['old_password'] = existing_user.password
                change_password_form['new_password'] = 'Test1234'
                change_password_form['confirm_new_password'] = 'Test1234'
                response = logged_in_client.post('/users/change_password', follow_redirects=True, data=change_password_form)
                assert response.status_code == 200

                assert len(templates) == 2
                template = templates[1][0]
                assert template.name == 'users/index.html'

                user_after_change = user_repository.get_by_id(existing_user.id)

                assert user_before_change.password_hash != user_after_change.password_hash

