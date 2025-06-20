from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from models import get_connection

topic_bp = Blueprint('topics', __name__)

@topic_bp.route('/topics', methods=['GET', 'POST'])
@login_required
def topics():
    with get_connection() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            subject_id = request.form['subject_id']
            topic_name = request.form['topic_name']
            cursor.execute('''
                INSERT INTO topics (subject_id, name, user_id) VALUES (?, ?, ?)
            ''', (subject_id, topic_name, current_user.id))
            conn.commit()
            return redirect('/topics')

        # Load user's subjects for dropdown
        cursor.execute('SELECT id, name FROM subjects WHERE user_id = ?', (current_user.id,))
        subjects = cursor.fetchall()

        # Load user's topics for table
        cursor.execute('''
            SELECT topics.id, topics.name, subjects.name 
            FROM topics 
            JOIN subjects ON topics.subject_id = subjects.id
            WHERE topics.user_id = ?
        ''', (current_user.id,))
        topics = cursor.fetchall()

    return render_template('topics.html', subjects=subjects, topics=topics)

@topic_bp.route('/topics/delete/<int:id>', methods=['POST'])
@login_required
def delete_topic(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM topics WHERE id=? AND user_id=?", (id, current_user.id))
        conn.commit()
    return redirect('/topics')
