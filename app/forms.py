from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, TextAreaField, FloatField
from wtforms.validators import InputRequired, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = EmailField('Email', validators= [InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators= [InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators= [InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class CoffeeForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    coffee_type = StringField('Type', validators=[InputRequired()])
    price = StringField('Price', validators=[InputRequired()])
    description = TextAreaField('Description')
    rating = FloatField('Rating')
    brew_method = StringField('Brew Method')
    roaster = StringField('Roaster')
    submit = SubmitField('Add Coffee')