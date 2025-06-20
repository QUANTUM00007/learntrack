from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from models import get_connection

subject_bp = Blueprint('subjects', __name__)

@subject_bp.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    if request.method == 'POST':
        name = request.form['name']
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subjects (name, user_id) VALUES (?, ?)", (name, current_user.id))
            conn.commit()
        return redirect('/subjects')

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects WHERE user_id = ?", (current_user.id))
        subjects = cursor.fetchall()
    return render_template('subjects.html', subjects=subjects)

from flask_login import login_required, current_user

@subject_bp.route('/subjects/delete/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id=? AND user_id=?", (id, current_user.id))
        cursor.execute("DELETE FROM logs WHERE subject_id=? AND user_id=?", (id, current_user.id))
        conn.commit()
    return redirect('/subjects')
