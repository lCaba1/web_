from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
import mysql.connector as connector

from .repositories import UserRepository, RoleRepository, JournalRepository
from . import db

from functools import wraps

import re

def validate_login(login):
    if len(login) < 5:
        return False, "Логин должен содержать не менее 5 символов"
    if not re.match(r'^[a-zA-Z0-9]+$', login):
        return False, "Логин должен содержать только латинские буквы и цифры"
    
    return True, None

def validate_password(password):
    if password == None or not password.strip():
        return False, "Поле не может быть пустым"
    if len(password) < 8:
        return False, "Пароль должен содержать не менее 8 символов"
    if len(password) > 128:
        return False, "Пароль должен содержать не более 128 символов"
    if ' ' in password:
        return False, "Пароль не должен содержать пробелов"
    if not re.search(r'[A-ZА-ЯЁ]', password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"
    if not re.search(r'[a-zа-яё]', password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"
    if not re.search(r'[0-9]', password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if re.search(r'[^a-zA-Zа-яА-ЯёЁ0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\'\.,:;]', password):
        return False, "Пароль содержит недопустимые символы"
    
    return True, None

def validate_user_data(user_data):

    errors = {}

    required_fields = ['username', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if user_data[field] == None or not user_data[field].strip():
        # if field not in user_data or not user_data[field].strip():
            # return False, f"Поле {field} не может быть пустым", field
            errors[field] = "Поле не может быть пустым" 
    
    login = user_data['username']
    password = user_data['password']

    if 'username' not in errors:
        validate_login_status, validate_login_message = validate_login(login)
        if not validate_login_status:
            errors['username'] = validate_login_message
    if 'password' not in errors:
        validate_password_status, validate_password_message = validate_password(password)
        if not validate_password_status:
            errors['password'] = validate_password_message

    return errors

def check_rights(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        
        if current_user.role == 'user':
            if f.__name__== 'edit' and kwargs.get('user_id') == current_user.id:
                return f(*args, **kwargs)
            if f.__name__ == 'show' and kwargs.get('user_id') == current_user.id:
                return f(*args, **kwargs)
            if f.__name__ == 'visitor_log':
                return f(*args, **kwargs)
            # if f.__name__ == 'change_password':
            #     return f(*args, **kwargs)
            
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('users.index'))
    return decorated_function 

user_repository = UserRepository(db)
role_repository = RoleRepository(db)
journal_repository = JournalRepository(db)

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
def index():
    return render_template('users/index.html', users=user_repository.all())

@bp.route('/visitor_log', methods=['GET', 'POST'])
@login_required
@check_rights
def visitor_log():
    if current_user.role != 'admin':    
        logs_count = journal_repository.get_total_count_by_user_id(current_user.id)
    else:
        logs_count = journal_repository.get_total_count()

    per_page = request.args.get('per_page')
    per_page = abs(int(per_page)) if per_page != None and per_page.isnumeric() else 10

    page = request.args.get('page')
    page = abs(int(page)) if page != None and page.isnumeric() else 1

    if page > (logs_count // per_page) + 1:
        page = 1

    if current_user.role != 'admin':
        logs = journal_repository.get_page_by_user_id(current_user.id, per_page, page)
    else:
        logs = journal_repository.get_page(per_page, page)

    return render_template('users/visitor_log.html', 
                           logs = logs, 
                           total_count = logs_count, 
                           per_page = per_page, 
                           page = page)

@bp.route('/<int:user_id>')
@login_required
@check_rights
def show(user_id):  
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))
    user_role = role_repository.get_by_id(user.role_id)
    return render_template('users/show.html', user_data=user, user_role=getattr(user_role, 'name'))

@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@check_rights
def delete(user_id):
    try:
        user_repository.delete(user_id)
        flash('Учётная запись успешно удалена', 'success')
    except connector.errors.DatabaseError:
        flash('Произошла ошибка при удалении записи. Попробуйте позже!', 'danger')
        db.connect().rollback()
    return redirect(url_for('users.index'))
    
@bp.route('/new', methods=['POST', 'GET'])
@login_required
@check_rights
def new():
    user_data = {}
    errors = {}

    if request.method == 'POST':
        fields = ['username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id']
        user_data = {field: request.form.get(field) or None for field in fields}
        errors = validate_user_data(user_data)
        if not errors:
            try:
                user_repository.create(**user_data)
                flash('Учётная запись успешно создана.', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены.', 'danger')
                db.connect().rollback()
    return render_template('users/new.html', user_data=user_data, roles=role_repository.all(), errors=errors)

@bp.route('/<int:user_id>/edit', methods=['POST', 'GET'])
@login_required
@check_rights
def edit(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))

    errors = {}

    if request.method == 'POST':
        fields = ('first_name', 'middle_name', 'last_name')
        user_data = {field: request.form.get(field) or None for field in fields}

        required_fields = ['first_name', 'last_name']
        for field in required_fields:
            if user_data[field] == None or not user_data[field].strip():
                errors[field] = "Поле не может быть пустым"

        if current_user.role == 'admin':
            user_data['role_id'] = request.form.get('role_id')
        else:
            user_data['role_id'] = role_repository.get_by_name(current_user.role).id

        user_data['user_id'] = user_id

        if not errors:
            try:
                user_repository.update(**user_data)
                flash('Учётная запись успешно изменена', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при изменении записи.', 'danger')
                db.connect().rollback()
                user = user_data

    return render_template('users/edit.html', user_data=user, roles=role_repository.all(), errors=errors)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():

    errors = {}

    if request.method == 'POST':
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")

        validate_password_status, validate_password_message = validate_password(new_password)
        if not validate_password_status:
            errors['new_password'] = validate_password_message
        
        if new_password != confirm_new_password:
            errors['confirm_new_password'] = 'Пароли не совпадают'

        username = user_repository.get_by_id(current_user.get_id())
        user = user_repository.get_by_username_and_password(username.username, old_password)
        if user is None:
            errors['old_password'] = 'Старый пароль указан неверно'

        if not errors:
            try:
                user_repository.update_password(current_user.get_id(), new_password)
                flash('Пароль успешно изменён!', 'success')
                return redirect(url_for('index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены.', 'danger')
                db.connect().rollback()

    return render_template('users/password.html', errors=errors)
