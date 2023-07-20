from flask import Flask, redirect, url_for, request, render_template
from sqlalchemy import func
from user.routers import user
from flask_login import LoginManager
from app_database.db_connect import session_maker
from app_database.models import User, Category, Post
from settings_env import secret_key
from datetime import timedelta
from category.routers import category
from post.routers import post
from post.forms import SearchForm

app = Flask(__name__)
app.secret_key = secret_key
app.permanent_session_lifetime = timedelta(minutes=10)
app.register_blueprint(user)
app.register_blueprint(category)
app.register_blueprint(post)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.user_login"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "info"


@app.route("/")
def index():
    """Home page"""
    return redirect(url_for("post.view_all_posts"))


@login_manager.user_loader
def load_user(user_id):
    """Get user"""
    with session_maker() as db_session:
        return db_session.get(User, user_id)


@app.before_request
def get_category():
    """Show categories in desired HTML-templates"""
    with session_maker() as db_session:
        category_post = db_session.query(Category.id, Category.title, func.count(Post.id).label("post_count")).join(
            Post).group_by(
            Category.id, Category.title).all()
    request.categories = category_post


@app.context_processor
def base():
    """Form Search"""
    form = SearchForm()
    return dict(form=form)


@app.template_filter('format_time')
def format_time(value):
    """Time Filter"""
    return value.strftime('%d-%m-%Y %H:%M')


@app.errorhandler(404)
def page_not_found(error):
    """Page 404"""
    response = {
        "title": "Page Not Found"
    }
    return render_template("page_404.html", response=response), 404


@app.errorhandler(500)
def page_error_server(error):
    """Page 500"""
    response = {
        "title": "Server Error"
    }
    return render_template("page_500.html", response=response), 500


if __name__ == "__main__":
    app.run()
