import sqlite3

DB_NAME = 'database.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Add this users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Create subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                hours REAL,
                log_date TEXT,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Create topics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Create goals table (optional but helpful)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                weekly_hours REAL NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

def get_connection():
    return sqlite3.connect(DB_NAME)
