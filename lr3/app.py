from datetime import timedelta
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации.'

def get_user():
    return {
        'id': '1',
        'login': 'user',
        'password': 'qwerty'
    }

class User(UserMixin):
    def __init__(self, id, login):
        self.id = id
        self.login = login

@login_manager.user_loader
def load_user(id):
    user = get_user()
    if id == user['id']:
        return User(user['id'], user['login'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/counter')
def counter():
    if session.get('count'):
        session['count'] += 1
    else:
        session['count'] = 1
    return render_template('counter.html', count = session['count'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    login = request.form.get('username')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me') == 'on'
    user = get_user()
    if user['login'] == login and user['password'] == password:
        user = User(user['id'], user['login'])
        login_user(user, remember = remember_me, duration = timedelta(days=7))
        flash('Успешный вход.')
        next = request.args.get('next')
        return redirect(next or url_for('index'))
    if login and password:
        flash('Неверно введённые данные.')
    return render_template('auth.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')
