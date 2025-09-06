from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SchoolForm(FlaskForm):
    name = StringField('School Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Add School')

class EditSchoolForm(FlaskForm):
    name = StringField('School Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Update School')

class ClassroomForm(FlaskForm):
    name = StringField('Classroom Name', validators=[DataRequired(), Length(max=100)])
    school = SelectField('School', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Classroom')

class ClassroomFormForSchool(FlaskForm):
    name = StringField('Classroom Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Add Classroom')

class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Add Student')

class EditClassroomForm(FlaskForm):
    name = StringField('Classroom Name', validators=[DataRequired(), Length(max=100)])
    school = SelectField('School', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Update Classroom')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
