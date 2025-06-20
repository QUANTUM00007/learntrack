from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required, UserMixin
import hashlib
from models import get_connection
import sqlite3

auth_bp = Blueprint('auth', __name__)

# Custom User class
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
            row = cursor.fetchone()

        if row:
            user = User(row[0], username)
            login_user(user)
            return redirect('/')
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        with get_connection() as conn:
            cursor = conn.cursor()
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash("Username already exists.")
            else:
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    flash("Registered successfully. Please login.")
                    return redirect('/login')
                except sqlite3.IntegrityError:
                    flash("Error creating user. Please try again.")
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
