from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from app_database.models import Category
from sqlalchemy import select
from app_database.db_connect import session_maker

with session_maker() as db_session:
    try:
        category_set = list()
        for category in db_session.scalars(select(Category)).all():
            category_set.append((category.id, category.title))
    except Exception as ex:
        raise SystemError(f"Error connect database {ex}")


class PostForm(FlaskForm):
    """Post Form"""
    title = StringField("Title:", validators=[
        DataRequired(), Length(min=3, max=40, message="Title must be between 3 and 40 characters")
    ])
    content = TextAreaField("Content:", validators=[DataRequired()], render_kw={"rows": 10})
    category_id = SelectField("Category:", validators=[DataRequired()], choices=category_set)
    submit = SubmitField("Submit:")


class SearchForm(FlaskForm):
    """Search Form"""
    search = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
