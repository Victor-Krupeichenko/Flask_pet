from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    """Post Form"""
    title = StringField("Title:", validators=[
        DataRequired(), Length(min=3, max=40, message="Title must be between 3 and 40 characters")
    ])
    content = TextAreaField("Content:", validators=[DataRequired()], render_kw={"rows": 10})
    category_id = SelectField("Category:", validators=[DataRequired()])
    submit = SubmitField("Submit:")


class SearchForm(FlaskForm):
    """Search Form"""
    search = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
