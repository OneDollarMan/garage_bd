from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, validators, SubmitField, DecimalField, SelectField, DateTimeLocalField, \
    PasswordField
from wtforms.validators import Length, NumberRange, InputRequired, Regexp, ValidationError, Optional

rus_length = Length(min=1, max=45, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')
rus_number_range = NumberRange(min=1, max=99999999999, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')
rus_input_required = InputRequired(message='Заполните поле')
rus_year_range = NumberRange(min=2000, max=2022, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')
rus_octane_range = NumberRange(min=72, max=100, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')
rus_amount_range = NumberRange(min=1, max=10000, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')


def date_check(form, field):
    if field.data < datetime.today():
        raise ValidationError('Введите не прошедшую дату')


class LoginForm(FlaskForm):
    login = StringField('login')
    password = PasswordField('password')
    remember_me = BooleanField('remember_me', default=False)


class CarForm(FlaskForm):
    brand = StringField('Бренд', [rus_input_required, rus_length])
    model = StringField('Модель', [rus_input_required, rus_length])
    plate = StringField('Госномер', [rus_input_required, Regexp(regex='^[АВЕКМНОРСТУХ]\d{3}(?<!000)[АВЕКМНОРСТУХ]{2}\d{2,3}$', message='Введите госномер вида А111АА11')])
    year = DecimalField('Год выпуска', [rus_input_required, rus_year_range])
    submit = SubmitField('Добавить')


class DriverForm(FlaskForm):
    username = StringField('Юзернейм', [rus_input_required, rus_length])
    password = StringField('Пароль', [rus_input_required, rus_length])
    fio = StringField('ФИО', [rus_input_required, rus_length])
    car = SelectField('Автомобиль', [rus_input_required])
    submit = SubmitField('Добавить')


class GasForm(FlaskForm):
    brand = StringField('Производитель', [rus_input_required, rus_length])
    octane = DecimalField('Октановое число', [rus_input_required, rus_octane_range])
    submit = SubmitField('Добавить')


class GasAddForm(FlaskForm):
    gas = SelectField('Топливо', [rus_input_required])
    amount = DecimalField('Количество', [rus_input_required, rus_amount_range])
    submit2 = SubmitField('Добавить')


class StationForm(FlaskForm):
    name = StringField('Название', [rus_input_required, rus_length])
    address = StringField('Адрес', [rus_input_required, rus_length])
    submit = SubmitField('Добавить')


class TransportationForm(FlaskForm):
    date = DateTimeLocalField('Дата отправления', format='%Y-%m-%dT%H:%M', validators=[rus_input_required, date_check])
    driver = SelectField('Водитель', [rus_input_required])
    gas = SelectField('Топливо', [rus_input_required])
    station = SelectField('Станция', [rus_input_required])
    amount = DecimalField('Количество', [rus_input_required, rus_amount_range])
    submit = SubmitField('Добавить')


class FilterForm(FlaskForm):
    start_date = DateTimeLocalField('От', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    end_date = DateTimeLocalField('До', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    driver2 = SelectField('Сортировка по водителю')
    status = SelectField('Сортировка по статусу')
    submit2 = SubmitField('Показать')
