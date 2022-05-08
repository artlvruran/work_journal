from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, TextAreaField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, InputRequired


class DepartmentForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = IntegerField('Chief id', validators=[InputRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')
