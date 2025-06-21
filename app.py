from flask import Flask, request
from flask_login import LoginManager
from models import init_db, get_connection
from api.auth_routes import auth_bp, User 
from api.subject_routes import subject_bp
from api.log_routes import log_bp
from api.dashboard_routes import dashboard_bp
from api.topics_route import topic_bp
from api.goals_routes import goal_bp
from dotenv import load_dotenv
import os, datetime, logging


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key")

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(user_id, row[0])  # ✅ Return a User object
        return None

@app.before_request
def log_visitor():
    logging.info(f"{datetime.datetime.now()} | IP: {request.remote_addr} | Agent: {request.user_agent}")

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(subject_bp)
app.register_blueprint(log_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(topic_bp)
app.register_blueprint(goal_bp)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
