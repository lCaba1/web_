def test_get_with_id_with_existing_user(user_repository, existing_user):
    user = user_repository.get_with_id(existing_user.id)
    assert user.id == existing_user.id
    assert user.login == existing_user.login
    
def test_get_with_id_with_nonexisting_user(user_repository, nonexisting_user):
    user = user_repository.get_with_id(nonexisting_user.id)
    assert user == None

def test_all_users_with_nonempty_db(user_repository, example_users):
    users = user_repository.get_all()
    assert len(users) == len(example_users)
    for loaded_user, example_user in zip(users, example_users):
        assert loaded_user.id == example_user.id
        assert loaded_user.login == example_user.login

def test_get_with_login_password_with_existing_user(user_repository, existing_user):
    user = user_repository.get_with_login_password(existing_user.login, existing_user.password)
    assert user.id == existing_user.id
    assert user.login == existing_user.login

def test_get_with_login_password_with_nonexisting_user(user_repository, nonexisting_user):
    user = user_repository.get_with_login_password(nonexisting_user.login, nonexisting_user.password)
    assert user == None