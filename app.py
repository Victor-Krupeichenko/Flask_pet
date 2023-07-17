from flask import Flask, render_template
from user.routers import user
from flask_login import LoginManager
from app_database.db_connect import session_maker
from app_database.models import User
from settings_env import secret_key
from datetime import timedelta

app = Flask(__name__)
app.secret_key = secret_key
app.permanent_session_lifetime = timedelta(minutes=10)
app.register_blueprint(user)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.user_login"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "info"


@app.route("/")
def index():
    """Home page"""
    response = {
        "title": "Flask Home Page"
    }
    return render_template("index.html", response=response)


@login_manager.user_loader
def load_user(user_id):
    """Get user"""
    with session_maker() as db_session:
        return db_session.get(User, user_id)
