from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from user.forms import RegisterUserForm, LoginUserForm
from app_database.db_connect import session_maker
from app_database.models import User
from sqlalchemy import select
from flask_login import login_user, logout_user, current_user, login_required

user = Blueprint("user", __name__, static_folder="static", template_folder="template")


def get_data_form_fields(form) -> dict:
    """Getting data from form fields"""
    user_data = dict()
    exclude_fields = ["password1", "password2", "csrf_token", "submit"]
    for field in form:
        if field.name not in exclude_fields:
            user_data.setdefault(field.name, field.data)
    user_data.update({"password_hash": request.form.get("password1")})
    return user_data


def get_errors(form, category_error="danger"):
    """Errors Fields"""
    for field, error in form.errors.items():
        flash(message=f"Error: field - {error.pop(0)}", category=category_error)


def get_error_database_flash_message(error, db_session, category_error="danger"):
    """Errors Database"""
    db_session.rollback()
    flash(message=f"Error: Connect Database -> {error}", category=category_error)


@user.route("/regiser-user", methods=["POST", "GET"])
def user_register():
    """Register user"""
    form = RegisterUserForm()
    response = {
        "title": "Register User",
        "register": True,

    }
    if request.method == "POST":
        if form.validate_on_submit():
            user_data = get_data_form_fields(form=form)
            with session_maker() as db_session:
                try:
                    create_user = User(**user_data)
                    db_session.add(create_user)
                    db_session.commit()
                    login_user(create_user)
                    session.permanent = True  # Сохраняет даные пользователя в сессии
                    flash(message="User create", category="success")
                    return redirect(url_for("index"))
                except Exception as ex:
                    get_error_database_flash_message(error=ex, db_session=db_session)
                    return render_template("user/register_user.html", response=response, form=form)
        else:
            get_errors(form)
    return render_template("user/register_user.html", response=response, form=form)


@user.route("/user-login", methods=["POST", "GET"])
def user_login():
    """User Logged"""
    response = {
        "title": "Login User",
        "login": True,
    }
    form = LoginUserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            with session_maker() as db_session:
                try:
                    user_found = db_session.scalars(
                        select(User).filter(User.username == request.form.get("username"))).first()
                    if not user_found:
                        flash(message=f"User: {request.form.get('username')} is not found", category="danger")
                        return render_template("user/login_user.html", response=response, form=form)
                    else:
                        if user_found.check_password(request.form.get("password")):
                            login_user(user_found)
                            session.permanent = True  # Сохраняет даные пользователя в сессии
                            flash(message=f"{request.form.get('username')} Successfully logged in", category="success")
                            return redirect(url_for('index'))
                        else:
                            flash(message="Incorrect password", category="danger")
                            return render_template("user/login_user.html", response=response, form=form)
                except Exception as ex:
                    get_error_database_flash_message(error=ex, db_session=db_session)
                    return render_template("user/login_user.html", response=response, form=form)
        else:
            get_errors(form)
    return render_template("user/login_user.html", response=response, form=form)


@user.route("/logout")
@login_required
def user_logout():
    """User Logged"""
    name = current_user.username
    logout_user()
    flash(message=f"{name} Logged out", category="info")
    return redirect(url_for('user.user_login'))


@user.route("/update-user", methods=["POST", "GET"])
@login_required
def user_update():
    """User update"""
    response = {
        "title": "Update User",
        "user_update": True
    }
    form = RegisterUserForm()
    with session_maker() as db_session:
        update_current_user = db_session.get(User, current_user.id)
        if request.method == "POST":
            if form.validate_on_submit():
                user_data = get_data_form_fields(form)
                try:
                    for key, value in user_data.items():
                        setattr(update_current_user, key, value)
                    db_session.commit()
                    flash(message="User Update Successfully", category="success")
                    return redirect(url_for("index"))
                except Exception as ex:
                    get_error_database_flash_message(error=ex, db_session=db_session)
                    return redirect(url_for("user.user_update"))
            else:
                get_errors(form)
    return render_template(
        "user/update_user.html", response=response, form=form, update_current_user=update_current_user
    )


@user.route("/delete-user/<int:user_id>")
@login_required
def user_delete(user_id):
    """User Delete"""
    with session_maker() as db_session:
        try:
            user_to_delete = db_session.get(User, user_id)
            username = user_to_delete.username
            db_session.delete(user_to_delete)
            db_session.commit()
            flash(message=f"User {username} deleted", category="info")
            return redirect(url_for("index"))
        except Exception as ex:
            get_error_database_flash_message(error=ex, db_session=db_session)
            return redirect(url_for("index"))
