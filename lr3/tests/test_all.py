from flask import session
from app import app as application
from datetime import timedelta, datetime, timezone



# Счётчик посещений работает корректно и для каждого пользователя выводит своё значение

def test_counter_for_single_user(client, captured_templates):
    with captured_templates as templates:
        for ind in range(5):
            response = client.get('/counter')
            assert response.status_code == 200
            assert templates[len(templates) - 1][0].name == 'counter.html'
            assert session['count'] == ind + 1
            assert f'Количество посещений вами данной страницы: {session['count']}' in response.text 

def test_counter_for_many_users(captured_templates):
    with captured_templates as templates:
        for _ in range(5):
            with application.test_client() as new_client:
                for ind in range(7):
                    response = new_client.get('/counter')
                    assert response.status_code == 200
                    assert templates[len(templates) - 1][0].name == 'counter.html'
                    assert session['count'] == ind + 1
                    assert f'Количество посещений вами данной страницы: {session['count']}' in response.text 



# После успешной аутентификации пользователь перенаправляется на главную страницу, ему показывается соответствующее сообщение

def test_successful_login(client, captured_templates, login_data):
    with captured_templates as templates:
        response = client.post('/login', follow_redirects=True, data=login_data[0])
        assert response.status_code == 200 
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'index.html'
        assert 'Успешный вход.' in response.text



# После неудачной попытки аутентификации пользователь остаётся на той же странице, ему показывается сообщение об ошибке

def test_unsuccessful_login(client, captured_templates, login_data):
    with captured_templates as templates:
        response = client.post('/login', data=login_data[1])
        assert response.status_code == 200 
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth.html'
        assert 'Неверно введённые данные.' in response.text



# Аутентифицированный пользователь имеет доступ к секретной странице

def test_access_secret_page_authenticated(logged_in_client, captured_templates):
    with captured_templates as templates:
        response = logged_in_client.get('/secret')
        assert response.status_code == 200
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'secret.html'
        assert 'Имеют доступ только аутентифицированные пользователи.' in response.text



# Неаутентифицированный (анонимный) пользователь при попытке доступа к секретной странице перенаправляется на страницу аутентификации с соответствующим сообщением

def test_access_secret_page_unauthenticated(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/secret', follow_redirects=True)
        assert response.status_code == 200
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth.html'
        assert 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации.' in response.text



# При аутентификации после неудачной попытки доступа к секретной странице пользователь автоматически перенаправляется на секретную страницу

def test_redirect_after_login(client, captured_templates, login_data):
    with captured_templates as templates:
        response = client.get('/secret', follow_redirects=True)
        assert response.status_code == 200
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth.html'
        assert 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации.' in response.text
        response = client.post(response.request.full_path, data=login_data[2], follow_redirects=True)
        assert response.status_code == 200
        assert len(templates) == 2
        template = templates[1][0]
        assert template.name == 'secret.html'
        assert 'Имеют доступ только аутентифицированные пользователи.' in response.text



# Параметр "Запомнить меня" работает корректно (устанавливается remember_token с заданным сроком хранения)

def test_remember_me(client, login_data):
    response = client.post('/login', data=login_data[0], follow_redirects=False)
    assert response.status_code == 302
    assert 'remember_token' in response.headers['Set-Cookie']
    correct_expires_date = datetime.now(timezone.utc) + timedelta(days=7)
    assert correct_expires_date.strftime("%d %b %Y") in response.headers['Set-Cookie']



# В навбаре корректно показываются/скрываются ссылки в зависимости от статуса пользователя (аутентифицирован или нет)

def test_navbar_links_before_login(client, captured_templates):
    with captured_templates as templates:
        response = client.get('/')
        assert response.status_code == 200
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'index.html'
        assert 'Счётчик посещений' in response.text 
        assert 'Войти' in response.text 
        assert 'Секретная страница' not in response.text
        assert 'Выйти' not in response.text

def test_navbar_links_after_login(logged_in_client, captured_templates):
    with captured_templates as templates:
        response = logged_in_client.get('/')
        assert response.status_code == 200
        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'index.html'
        assert 'Секретная страница' in response.text 
        assert 'Счётчик посещений' in response.text 
        assert 'Выйти' in response.text
        assert 'Войти' not in response.text 
