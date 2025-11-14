from flask_login import current_user

def test_page_report_unathorized(client, captured_templates, existing_user):
    with captured_templates as templates:
        response = client.get('/reports/pages', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_page_report_authorized_as_user(client_logged_as_user, captured_templates, example_logs, journal_repository):
    with captured_templates as templates:
        response = client_logged_as_user.get(f'/reports/pages')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'reports/pages.html'

        assert 'Статистика по страницам' in response.text

        statistics = journal_repository.log_page_aggregation(current_user.id)
        for stat in statistics:
            assert stat.path in response.text
            assert str(stat.number_of_visits) in response.text

def test_page_report_authorized_as_admin(client_logged_as_admin, captured_templates, example_logs, journal_repository):
    with captured_templates as templates:
        response = client_logged_as_admin.get(f'/reports/pages')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'reports/pages.html'

        assert 'Статистика по страницам' in response.text

        statistics = journal_repository.log_page_aggregation()
        for stat in statistics:
            assert stat.path in response.text
            assert str(stat.number_of_visits) in response.text
###################################################################################
def test_user_report_unathorized(client, captured_templates, existing_user):
    with captured_templates as templates:
        response = client.get('/reports/users', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_user_report_authorized_as_user(client_logged_as_user, captured_templates, example_logs, journal_repository):
    with captured_templates as templates:
        response = client_logged_as_user.get(f'/reports/users')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'reports/users.html'

        assert 'Статистика по пользователям' in response.text

        statistics = journal_repository.log_user_aggregation(current_user.id)
        for stat in statistics:
            assert stat.user_full_name in response.text
            assert str(stat.number_of_visits) in response.text

def test_page_report_authorized_as_admin(client_logged_as_admin, captured_templates, example_logs, journal_repository):
    with captured_templates as templates:
        response = client_logged_as_admin.get(f'/reports/users')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'reports/users.html'

        assert 'Статистика по пользователям' in response.text

        statistics = journal_repository.log_user_aggregation()
        for stat in statistics:
            assert stat.user_full_name in response.text
            assert str(stat.number_of_visits) in response.text

################################################################

def test_page_csv_export_as_user(client_logged_as_user, example_logs, journal_repository):
    response = client_logged_as_user.post(f'/reports/pages', follow_redirects=True)
    assert response.status_code == 200
    
    statistics = journal_repository.log_page_aggregation(current_user.id)

    csv_data = response.data.decode('utf-8').splitlines()
    assert len(csv_data) == 1 + len(statistics)

    assert csv_data[0] == 'Страница,Количество посещений'
    for index, stat in enumerate(statistics):
        assert csv_data[index + 1] == f'{stat.path},{stat.number_of_visits}'
    

def test_page_csv_export_as_admin(client_logged_as_admin, example_logs, journal_repository):
    response = client_logged_as_admin.post(f'/reports/pages', follow_redirects=True)
    assert response.status_code == 200
    
    statistics = journal_repository.log_page_aggregation()

    csv_data = response.data.decode('utf-8').splitlines()
    assert len(csv_data) == 1 + len(statistics)

    assert csv_data[0] == 'Страница,Количество посещений'
    for index, stat in enumerate(statistics):
        assert csv_data[index + 1] == f'{stat.path},{stat.number_of_visits}'

###############################################################

def test_user_csv_export_as_user(client_logged_as_user, example_logs, journal_repository):
    response = client_logged_as_user.post(f'/reports/users', follow_redirects=True)
    assert response.status_code == 200
    
    statistics = journal_repository.log_user_aggregation(current_user.id)

    csv_data = response.data.decode('utf-8').splitlines()
    assert len(csv_data) == 1 + len(statistics)

    assert csv_data[0] == 'Пользователь,Количество посещений'
    for index, stat in enumerate(statistics):
        assert csv_data[index + 1] == f'{stat.user_full_name},{stat.number_of_visits}'
    

def test_user_csv_export_as_admin(client_logged_as_admin, example_logs, journal_repository):
    response = client_logged_as_admin.post(f'/reports/users', follow_redirects=True)
    assert response.status_code == 200
    
    statistics = journal_repository.log_user_aggregation()

    csv_data = response.data.decode('utf-8').splitlines()
    assert len(csv_data) == 1 + len(statistics)

    assert csv_data[0] == 'Пользователь,Количество посещений'
    for index, stat in enumerate(statistics):
        assert csv_data[index + 1] == f'{stat.user_full_name},{stat.number_of_visits}'