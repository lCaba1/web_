import click
from flask import current_app
from . import db

@click.command('initdb')
def initdb_command():
    with current_app.open_resource('initdb.sql') as f:
        connection = db.connect()
        with connection.cursor() as cursor:
            sql_script = f.read().decode('utf8')
            queries = [q.strip() for q in sql_script.split(';') if q.strip()]
            for query in queries:
                if query: 
                    cursor.execute(query)
        connection.commit()
