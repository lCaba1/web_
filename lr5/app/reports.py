from flask import Blueprint, request, render_template, Response
from .repositories import JournalRepository
from . import db
from flask_login import login_required, current_user
import csv
from io import StringIO

journal_repository = JournalRepository(db)
bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/pages', methods = ['GET', 'POST'])
@login_required
def pages():
    if current_user.role == 'admin':
        statistics = journal_repository.log_page_aggregation()
    else:
        statistics = journal_repository.log_page_aggregation(current_user.id)      
    if request.method == 'POST':    
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Страница", "Количество посещений"])
        for stat in statistics:
            writer.writerow([stat.path, stat.number_of_visits])
        response = Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=pages_stat.csv"}
        )
        return response
    return render_template('reports/pages.html', statistics=statistics)

@bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.role == 'admin':
        statistics = journal_repository.log_user_aggregation()
    else:
        statistics = journal_repository.log_user_aggregation(current_user.id)
    if request.method == 'POST':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Пользователь", "Количество посещений"])
        for stat in statistics:
            writer.writerow([stat.user_full_name, stat.number_of_visits]) 
        response = Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=users_stat.csv"}
        )
        return response
    return render_template('reports/users.html', statistics=statistics)
