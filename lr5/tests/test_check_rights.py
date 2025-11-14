from flask_login import current_user

def test_check_view_rights_as_user(example_users, client_logged_as_user, captured_templates):
    with captured_templates as templates:

        response = client_logged_as_user.get(f'/users/{example_users[1].id}')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/show.html'

        assert example_users[1].first_name in response.text
        assert example_users[1].last_name in response.text

        response = client_logged_as_user.get(f'/users/{example_users[0].id}', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 2
        template = templates[1][0]
        assert template.name == 'users/index.html'

        assert 'У вас недостаточно прав для доступа к данной странице.' in response.text

def test_check_view_rights_as_admin(example_users, client_logged_as_admin, captured_templates):
    with captured_templates as templates:
        response = client_logged_as_admin.get(f'/users/{example_users[0].id}')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/show.html'

        assert example_users[0].first_name in response.text
        assert example_users[0].last_name in response.text

        response = client_logged_as_admin.get(f'/users/{example_users[1].id}', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 2
        template = templates[1][0]
        assert template.name == 'users/show.html'

        assert example_users[1].first_name in response.text
        assert example_users[1].last_name in response.text

def test_check_edit_rights_as_user(example_users, client_logged_as_user, captured_templates):
    with captured_templates as templates:

        response = client_logged_as_user.get(f'/users/{example_users[1].id}/edit')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/edit.html'

        assert example_users[1].first_name in response.text
        assert example_users[1].last_name in response.text

        response = client_logged_as_user.get(f'/users/{example_users[0].id}/edit', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 2
        template = templates[1][0]
        assert template.name == 'users/index.html'

        assert 'У вас недостаточно прав для доступа к данной странице.' in response.text

def test_check_edit_rights_as_admin(example_users, client_logged_as_admin, captured_templates):
    with captured_templates as templates:
        response = client_logged_as_admin.get(f'/users/{example_users[0].id}/edit')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/edit.html'

        assert example_users[0].first_name in response.text
        assert example_users[0].last_name in response.text

        response = client_logged_as_admin.get(f'/users/{example_users[1].id}/edit', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 2
        template = templates[1][0]
        assert template.name == 'users/edit.html'

        assert example_users[1].first_name in response.text
        assert example_users[1].last_name in response.text

def test_check_delete_rights_as_user(example_users, client_logged_as_user, captured_templates):
    with captured_templates as templates:

        response = client_logged_as_user.post(f'/users/{example_users[1].id}/delete', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'У вас недостаточно прав для доступа к данной странице.' in response.text

def test_check_delete_rights_as_admin(example_users, client_logged_as_admin, captured_templates):
    with captured_templates as templates:
        response = client_logged_as_admin.post(f'/users/{example_users[1].id}/delete', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'Пользователь удален.' in response.text

def test_check_create_rights_as_admin(client_logged_as_admin, captured_templates, user_repository, existing_admin):
    with captured_templates as templates:
        response = client_logged_as_admin.get('/users/new', follow_redirects=True)
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
        new_user_data['role_id'] = '3'
        response = client_logged_as_admin.post('/users/new', follow_redirects=True, data=new_user_data)

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

'''
def test_check_create_rights_as_user(client_logged_as_user, captured_templates, user_repository, existing_user):
    with captured_templates as templates:
        response = client_logged_as_user.get('/users/new', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'

        assert 'У вас недостаточно прав для доступа к данной странице.' in response.text
'''
