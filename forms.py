from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Re-enter Password', 
                             validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[Optional()])
    birthday = DateField('Birthday (Optional)', validators=[Optional()])
    submit = SubmitField('Sign Up')

class QuestionnaireForm(FlaskForm):
    mental_illness = TextAreaField('Do you have any diagnosed mental illness?', 
                                  validators=[Optional()])
    preferred_therapist_gender = SelectField('Preferred therapist gender', 
                                           choices=[('', 'No preference'), 
                                                   ('male', 'Male'), 
                                                   ('female', 'Female'), 
                                                   ('non-binary', 'Non-binary')])
    preferred_language = SelectField('Preferred language', 
                                   choices=[('english', 'English'), 
                                           ('spanish', 'Spanish'), 
                                           ('french', 'French'),
                                           ('other', 'Other')])
    submit = SubmitField('Submit')