from flask import Blueprint, render_template, request, redirect, send_file
from flask_login import login_required, current_user
from models import get_connection
from flask import Response
import csv
import io


log_bp = Blueprint('logs', __name__)

@log_bp.route('/logs', methods=['GET', 'POST'])
@login_required
def log_study():
    with get_connection() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            subject_id = request.form['subject_id']
            hours = request.form['hours']
            log_date = request.form['log_date']
            cursor.execute("INSERT INTO logs (subject_id, hours, log_date, user_id) VALUES (?, ?, ?, ?)",
                           (subject_id, hours, log_date, current_user.id))
            conn.commit()
            return redirect('/logs')

        # Fetch subjects
        cursor.execute("SELECT id, name FROM subjects WHERE user_id=?", (current_user.id,))
        subjects = cursor.fetchall()

        # Fetch logs
        cursor.execute('''
            SELECT logs.id, subjects.name, logs.hours, logs.log_date
            FROM logs
            JOIN subjects ON logs.subject_id = subjects.id
            WHERE logs.user_id = ?
            ORDER BY logs.log_date DESC
        ''', (current_user.id,))
        logs = cursor.fetchall()

    return render_template('logs.html', subjects=subjects, logs=logs)

@log_bp.route('/logs/delete/<int:id>', methods=['POST'])
@login_required
def delete_log(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs WHERE id=? AND user_id=?", (id, current_user.id))
        conn.commit()
    return redirect('/logs')

@log_bp.route('/logs/download')
@login_required
def download_logs():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT subjects.name, logs.hours, logs.log_date
            FROM logs
            JOIN subjects ON logs.subject_id = subjects.id
            WHERE logs.user_id = ?
            ORDER BY logs.log_date DESC
        ''', (current_user.id,))
        logs = cursor.fetchall()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Subject', 'Hours', 'Date'])  # Header
    writer.writerows(logs)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='study_logs.csv'
    )
