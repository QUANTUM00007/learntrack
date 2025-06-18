# app.py
from flask import Flask, render_template, request, redirect
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_NAME = 'database.db'

# Initialize DB if not exists
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL)
                       ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            subject_id INTEGER,
                            hours REAL,
                            log_date TEXT,
                            FOREIGN KEY(subject_id) REFERENCES subjects(id))
                       ''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'POST':
        name = request.form['name']
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            conn.commit()
        return redirect('/subjects')
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
    return render_template('add_subject.html', subjects=subjects)

@app.route('/log', methods=['POST'])
def log():
    subject_id = request.form['subject_id']
    hours = request.form['hours']
    log_date = request.form['log_date']

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (subject_id, hours, log_date) VALUES (?, ?, ?)",
                       (subject_id, hours, log_date))
        conn.commit()
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT s.name, SUM(l.hours) FROM logs l
                          JOIN subjects s ON l.subject_id = s.id
                          GROUP BY l.subject_id''')
        stats = cursor.fetchall()
    return render_template('dashboard.html', stats=stats)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
