from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms import StringField, SubmitField
from app_database.db_connect import session_maker
from sqlalchemy import select
from app_database.models import Category


class CategoryForm(FlaskForm):
    """Create Category"""
    title = StringField("Title:", validators=[
        DataRequired(), Length(min=3, max=25, message="Title must be between 3 and 25 characters")
    ])
    submit = SubmitField("Create Category")

    def validate_title(self, form_title):
        """Validate title"""
        with session_maker() as db_session:
            result = db_session.scalars(select(Category).filter(Category.title == form_title.data)).first()
            if result:
                raise ValidationError(f"A category with the same name already exists")
