import sqlite3

DB_NAME = 'database.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Create subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                hours REAL,
                log_date TEXT,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        ''')

        # Create topics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        ''')

        # Create goals table (optional but helpful)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                weekly_hours REAL NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        ''')

def get_connection():
    return sqlite3.connect(DB_NAME)
