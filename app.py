# app.py
from flask import Flask, render_template, request, redirect
from models import init_db, get_connection

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


if __name__ == '__main__':
    init_db()  # Initialize DB if not already
    app.run(debug=True)
