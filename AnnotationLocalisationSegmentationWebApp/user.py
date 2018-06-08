#!/usr/bin/python
from werkzeug.security import check_password_hash

#from flask_wtf import Form
from wtforms import Form, StringField, PasswordField
from wtforms.validators import DataRequired


class User():
    def __init__(self, username):
        self.username = username


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

class LoginForm(Form):
    """Login form to access """

    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

