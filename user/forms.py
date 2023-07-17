from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app_database.db_connect import session_maker
from sqlalchemy import select
from app_database.models import User
from flask_login import current_user


# pip install email_validator


class RegisterUserForm(FlaskForm):
    """Form register and update user"""
    username = StringField("UserName: ", validators=[
        DataRequired(), Length(min=3, max=30, message="Doesn't match length")
    ], render_kw={"placeholder": "Username"})
    email = EmailField("Email:", validators=[
        DataRequired(), Email(message="Email is not correct"),
        Length(max=120, message="Email length must not exceed 120 characters")
    ], render_kw={"placeholder": "Email"})
    password1 = PasswordField("Password:", validators=[
        DataRequired(), Length(min=7, message="Password length must be at least 7 characters")
    ], render_kw={"placeholder": "Password"})
    password2 = PasswordField("Confirm Password:", validators=[
        DataRequired(), EqualTo("password1", message="Password mismatch")
    ], render_kw={"placeholder": "Confirm password"})
    submit = SubmitField("Register User")

    def validate_username(self, form_username):
        """Validete name"""
        with session_maker() as db_session:
            user = db_session.scalars(select(User).filter(User.username == form_username.data)).first()
            if user:
                raise ValidationError(
                    f"Username: ->{form_username.data}<- alredy exists! Please try a different username")

    def validate_email(self, form_email):
        """Validate email"""
        with session_maker() as db_session:
            user_email = db_session.scalars(select(User).filter(User.email == form_email.data)).first()
            if current_user.is_authenticated:
                if user_email and current_user.email != user_email.email:
                    raise ValidationError(
                        f"Email Addres: ->{form_email.data}<- alredy exists! Please try a different email address")
            else:
                if user_email:
                    raise ValidationError(
                        f"Email Addres: ->{form_email.data}<- alredy exists! Please try a different email address")


class LoginUserForm(FlaskForm):
    """Form login user"""
    username = StringField("UserName:", validators=[
        DataRequired(), Length(min=3, max=30, message="Doesn't match length")
    ], render_kw={"placeholder": "Username"})
    password = PasswordField("Password", validators=[
        DataRequired(), Length(min=7, message="Password length must be at least 7 characters")
    ], render_kw={"placeholder": "Password"})
    submit = SubmitField("Log in")
