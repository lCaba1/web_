# На странице "Параметры URL" отображаются все переданные в запросе параметры

def test_url_params(client, test_data):
    params = '?'
    for key, value in test_data['test_url_params'].items():
        params += key + '=' + value + '&'
    response = client.get(f'/url_params{params}')
    for key, value in test_data['test_url_params'].items():
        assert key in response.text
        assert value in response.text



# На странице "Заголовки запроса" отображаются все заголовки запроса (названия и значения)

def test_request_headers(client, test_data):
    headers = test_data['test_request_headers']
    response = client.get('/request_headers', headers = headers)
    for key, value in response.request.headers.items():
        assert key in response.text
        assert value in response.text



# На странице "Cookie" корректно устанавливается и удаляется значение куки в соответствии с заданием

def test_cookie(client, mocker, test_data):
    mocker.patch(
        'app.get_cookie',
        return_value = test_data['test_cookie'],
        autospec = True
    )
    response_1 = client.get('/cookie')
    response_2 = client.get('/cookie')
    cookies_1 = response_1.headers.getlist('Set-Cookie')
    cookies_2 = response_2.headers.getlist('Set-Cookie')
    for key, value in test_data['test_cookie'].items():
        assert any(f'{key}={value}' in c for c in cookies_1)
        assert any(f'{key}=;' in c for c in cookies_2)
        assert key not in response_1.text
        assert value not in response_1.text
        assert key in response_2.text
        assert value in response_2.text



# На странице "Параметры формы" отображаются введённые пользователем значения после отправки формы

def test_form_params(client, test_data):
    params = test_data['test_form_params']
    response = client.post('/form_params', data = params)
    for key, value in params.items():
        assert key in response.text
        assert value in response.text



# Валидация и форматирование номера телефона работают коррекно при любых возможных входных данных (проверить принципиально различные варианты)

def test_process_phone_number(client, test_data):
    from app import process_phone_number
    input = test_data['test_error_handling_form']['input']
    output = test_data['test_error_handling_form']['output']
    for key in input:
        for value in input[key]:
            assert process_phone_number(value) == output[value]



# На странице с валидацией номера телефона в случае возникновения ошибки выводится соответствующее сообщение об ошибке и используются соответствующие классы Bootstrap (см. задание)
# На странице с валидацией номера телефона в случае ввода корректного номера выводится отформатированный номер

def test_error_handling_form(client, test_data):
    input = test_data['test_error_handling_form']['input']
    output = test_data['test_error_handling_form']['output']
    for key in input:
        for value in input[key]:
            response = client.post('/error_handling_form', data = {key: value})
            assert output[value] in response.text
        
def test_error_handling_form(client, test_data):
    input = test_data['test_error_handling_form']['input']
    for key in input:
        for value in input[key]:
            response = client.post('/error_handling_form', data = {key: value})
            assert 'invalid-feedback' in response.text
            if value in response.text:
                assert 'is-invalid' in response.text
            else:
                assert 'is-invalid' not in response.text
