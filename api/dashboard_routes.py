from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import get_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Study summary stats
        cursor.execute('''
            SELECT s.name, SUM(l.hours)
            FROM logs l
            JOIN subjects s ON l.subject_id = s.id
            WHERE l.user_id = ?
            GROUP BY l.subject_id
        ''', (current_user.id,))
        stats = cursor.fetchall()

        # Goals with hours logged
        cursor.execute('''
            SELECT g.subject_id, s.name, g.weekly_hours, IFNULL(SUM(l.hours), 0)
            FROM goals g
            JOIN subjects s ON g.subject_id = s.id
            LEFT JOIN logs l ON g.subject_id = l.subject_id AND l.user_id = g.user_id
            WHERE g.user_id = ?
            GROUP BY g.subject_id
        ''', (current_user.id,))
        detailed_goals_raw = cursor.fetchall()

        detailed_goals = []
        for row in detailed_goals_raw:
            detailed_goals.append({
                "id": row[0],
                "name": row[1],
                "goal": row[2],
                "logged": row[3]
            })

        # Topics grouped by subject
        cursor.execute('''
            SELECT s.name, t.name
            FROM topics t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.user_id = ?
        ''', (current_user.id,))
        topics_raw = cursor.fetchall()

        topic_data = {}
        for subject_name, topic_name in topics_raw:
            topic_data.setdefault(subject_name, []).append(topic_name)

    return render_template('dashboard.html', stats=stats, detailed_goals=detailed_goals, topic_data=topic_data)
