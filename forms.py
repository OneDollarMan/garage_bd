from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, validators


class LoginForm(FlaskForm):
    login = StringField('login')
    password = StringField('password')
    remember_me = BooleanField('remember_me', default=False)


class RegForm(FlaskForm):
    username = StringField('username')
    fio = StringField('fio')
    password = StringField('password')
