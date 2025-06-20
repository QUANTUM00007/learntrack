from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from models import get_connection

goal_bp = Blueprint('goals', __name__)

@goal_bp.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    with get_connection() as conn:
        cursor = conn.cursor()

        # POST logic
        if request.method == 'POST':
            subject_id = request.form['subject_id']
            weekly_hours = request.form['weekly_hours']

            cursor.execute("SELECT id FROM goals WHERE subject_id = ? AND user_id = ?", (subject_id, current_user.id))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("UPDATE goals SET weekly_hours = ? WHERE subject_id = ? AND user_id = ?",
                               (weekly_hours, subject_id, current_user.id))
                flash("Goal updated successfully.")
            else:
                cursor.execute("INSERT INTO goals (subject_id, weekly_hours, user_id) VALUES (?, ?, ?)",
                               (subject_id, weekly_hours, current_user.id))
                flash("Goal added successfully.")

            conn.commit()
            return redirect('/goals')

        # GET data
        cursor.execute("SELECT id, name FROM subjects WHERE user_id = ?", (current_user.id,))
        subjects = cursor.fetchall()

        cursor.execute('''
            SELECT g.id, s.name, g.weekly_hours,
                IFNULL((
                    SELECT SUM(hours) FROM logs 
                    WHERE subject_id = g.subject_id AND user_id = ?
                ), 0) as total_hours
            FROM goals g
            JOIN subjects s ON g.subject_id = s.id
            WHERE g.user_id = ?
        ''', (current_user.id, current_user.id))
        goals = cursor.fetchall()

    return render_template('goals.html', goals=goals, subjects=subjects)

@goal_bp.route('/goals/delete/<int:id>', methods=['POST'])
@login_required
def delete_goal(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (id, current_user.id))
        conn.commit()
    flash("Goal deleted.")
    return redirect('/goals')
