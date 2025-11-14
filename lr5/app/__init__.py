from flask import Flask
from .dbconnector import DBConnector

db = DBConnector()

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = False)

    app.config.from_pyfile('config.py', silent = False)
    if test_config:
        app.config.from_mapping(test_config)

    db.init_app(app)

    from .initdb import initdb_command
    app.cli.add_command(initdb_command)

    from . import auth
    app.register_blueprint(auth.bp)
    auth.login_manager.init_app(app)

    from . import users
    app.register_blueprint(users.bp)
    app.route('/', endpoint = 'index')(users.index)

    from . import reports
    app.register_blueprint(reports.bp)

    if not test_config:
        from .repositories import JournalRepository
        from flask_login import current_user
        import mysql.connector as connector
        from flask import request

        journal_repository = JournalRepository(db)

        @app.before_request
        def visitor_logging():    
            visit_path = request.path
            forbidden_ext = ['.css', '.js', '.ico']
            if not any([ext in visit_path for ext in forbidden_ext]):
                if current_user.is_authenticated:
                    user_id = current_user.id
                else:
                    user_id = None
                try:
                    journal_repository.create(visit_path, user_id)
                except connector.errors.DatabaseError:
                    print('Ошибка записи в журнал.')
                    db.connect().rollback()

    return app
