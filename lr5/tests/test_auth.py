def test_successful_login(client, captured_templates, existing_user):
    with captured_templates as templates:
        login_data = {}
        login_data['login'] = existing_user.login
        login_data['password'] = existing_user.password
        response = client.post('/auth/login', follow_redirects=True, data=login_data)

        assert response.status_code == 200 
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/index.html'
        
        assert 'Успешный вход.' in response.text

def test_unsuccessful_login(client, captured_templates, nonexisting_user):
    with captured_templates as templates:
        login_data = {}
        login_data['login'] = nonexisting_user.login
        login_data['password'] = nonexisting_user.password
        response = client.post('/auth/login', follow_redirects=True, data=login_data)

        assert response.status_code == 200 
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'
        
        assert 'Неверно введённые данные.' in response.text