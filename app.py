# app.py
from flask import Flask, render_template, request, redirect
from models import init_db, get_connection
import csv
import io
from flask import send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'POST':
        name = request.form['name']
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            conn.commit()
        return redirect('/subjects')

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
    return render_template('subjects.html', subjects=subjects)

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        # First delete any logs associated with this subject
        cursor.execute("DELETE FROM logs WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM topics WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
    return redirect('/subjects')

@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        hours = request.form['hours']
        log_date = request.form['log_date']

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs (subject_id, hours, log_date) VALUES (?, ?, ?)",
                           (subject_id, hours, log_date))
            conn.commit()
        return redirect('/dashboard')

    # On GET: Fetch subjects for dropdown
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM subjects")
        subjects = cursor.fetchall()

    return render_template('log.html', subjects=subjects)

@app.route('/dashboard')
def dashboard():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Study time stats
        cursor.execute('''
            SELECT s.name, IFNULL(SUM(l.hours), 0)
            FROM subjects s
            LEFT JOIN logs l ON l.subject_id = s.id
            GROUP BY s.id
        ''')
        stats = cursor.fetchall()

        # Topics per subject
        cursor.execute('''
            SELECT s.name, t.name
            FROM topics t
            JOIN subjects s ON s.id = t.subject_id
        ''')
        topics = cursor.fetchall()

        # Goals
        cursor.execute('''
            SELECT s.name, g.weekly_hours
            FROM goals g
            JOIN subjects s ON s.id = g.subject_id
        ''')
        goals = cursor.fetchall()

    return render_template('dashboard.html', stats=stats, topics=topics, goals=goals)


@app.route('/topics', methods=['GET', 'POST'])
def topics():
    from models import get_connection  # Optional: just to be safe if not imported globally

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM subjects")
        subjects = cursor.fetchall()

    if request.method == 'POST':
        subject_id = request.form['subject_id']
        topic_name = request.form['topic_name']

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO topics (subject_id, name) VALUES (?, ?)", (subject_id, topic_name))
            conn.commit()
        return redirect('/topics')

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.name, s.name 
            FROM topics t 
            JOIN subjects s ON t.subject_id = s.id
        ''')
        topics_list = cursor.fetchall()

    return render_template('topics.html', topics=topics_list, subjects=subjects)

@app.route('/dashboard/download_csv')
def download_dashboard_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Subject Name', 'Total Hours'])

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.name, SUM(l.hours)
            FROM logs l
            JOIN subjects s ON l.subject_id = s.id
            GROUP BY l.subject_id
        ''')
        for row in cursor.fetchall():
            writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='dashboard_summary.csv')

@app.route('/logs/download_csv')
def download_logs_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Subject', 'Hours', 'Date'])

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.name, l.hours, l.log_date
            FROM logs l
            JOIN subjects s ON l.subject_id = s.id
            ORDER BY l.log_date DESC
        ''')
        for row in cursor.fetchall():
            writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='study_logs.csv')

@app.route('/logs')
def logs():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.id, s.name, l.hours, l.log_date
            FROM logs l
            JOIN subjects s ON l.subject_id = s.id
            ORDER BY l.log_date DESC
        ''')
        logs = cursor.fetchall()
    return render_template('logs.html', logs=logs)

@app.route('/logs/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs WHERE id = ?", (log_id,))
        conn.commit()
    return redirect('/logs')


if __name__ == '__main__':
    init_db()  # Initialize DB if not already
    app.run(debug=True)
