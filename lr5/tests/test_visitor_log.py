from flask_login import current_user

def test_visitor_log_unathorized(client, captured_templates, existing_user):
    with captured_templates as templates:
        response = client.get('/users/visitor_log', follow_redirects=True)
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'auth/auth.html'

def test_visitor_log_authorized_as_user(client_logged_as_user, captured_templates, example_logs):
    with captured_templates as templates:
        response = client_logged_as_user.get(f'/users/visitor_log?per_page={len(example_logs)}')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/visitor_log.html'

        assert 'Журнал посещений' in response.text

        for log in example_logs:
            if log.user_id == current_user.id:
                assert log.path in response.text
            else:
                assert log.path not in response.text

def test_visitor_log_authorized_as_admin(client_logged_as_admin, captured_templates, example_logs):
    with captured_templates as templates:
        response = client_logged_as_admin.get(f'/users/visitor_log?per_page={len(example_logs)}')
        assert response.status_code == 200

        assert len(templates) == 1
        template = templates[0][0]
        assert template.name == 'users/visitor_log.html'

        assert 'Журнал посещений' in response.text

        for log in example_logs:
            assert log.path in response.text