from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, TextAreaField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, InputRequired


class AddJobForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    team_leader_id = IntegerField('Team Leader id', validators=[InputRequired()])
    work_size = IntegerField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is job finished?')
    submit = SubmitField('Submit')