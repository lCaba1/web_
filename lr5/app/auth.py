from flask import Blueprint, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user
from .repositories import UserRepository, RoleRepository
from . import db


user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации.'

class User(UserMixin):
    def __init__(self, id, login, role_id):
        self.id = id
        self.login = login
        self.role = role_repository.get_with_id(role_id).name

@login_manager.user_loader
def load_user(id):
    user = user_repository.get_with_id(id)
    if user is not None:
        return User(user.id, user.login, user.role_id)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me') == 'on'
    user = user_repository.get_with_login_password(login, password)
    if user is not None:
        login_user(User(user.id, user.login, user.role_id), remember = remember_me)
        flash('Успешный вход.')
        next = request.args.get('next')
        return redirect(next or url_for('users.index'))
    if login and password:
        flash('Неверно введённые данные.')
    return render_template('auth/auth.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.index'))
