import hashlib
import pyotp
from flask import url_for, render_template, request, redirect, send_from_directory, flash, session
from __init__ import app
import forms
import repo

gr = repo.GarageRepo(host=app.config['HOST'], user=app.config['USER'], password=app.config['PASSWORD'], db=app.config['DB'])  # Создание объекта репозитория


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error)


@app.route("/")
def index():
    return render_template('index.html', title="Главная",
                           counts=[gr.get_cars_count(), gr.get_users_count(), gr.get_gases_count(),
                                   gr.get_stations_count(), gr.get_transportations_count()])


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('loggedin'):
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = gr.login_user(form.login.data, hashlib.md5(form.password.data.encode('utf-8')).hexdigest())
        if user:
            user = user[0]
            if user[6]:
                if pyotp.TOTP(user[7]).verify(form.otp.data):
                    flash('Вы авторизовались!')
                    session['loggedin'] = True
                    session['id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = user[4]
                else:
                    flash('Неправильный OTP')
            else:
                flash('Вы авторизовались!')
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[4]
            return redirect(url_for('login'))
        else:
            flash('Пользователя с данной связкой логин-пароль не существует!')
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/2fa", methods=['GET', 'POST'])
def fa():
    if session.get('loggedin'):
        form = forms.FaForm()
        user = gr.get_user(session.get('username'))[0]

        if form.validate_on_submit():
            if pyotp.TOTP(user[7]).verify(form.otp.data):
                if gr.toggle_2fa(user[0]):
                    flash('Двойная аутентификация включена')
                else:
                    flash('Двойная аутентификация выключена')
            else:
                flash('Неправильный OTP')
            return redirect(url_for('fa'))
        return render_template("2fa.html", title='Двухфакторная аутентификация', enable=user[6], secret=user[7], form=form, url=pyotp.totp.TOTP(user[7]).provisioning_uri(name=session.get('username'), issuer_name='Гараж'))
    else:
        flash('Требуется аутентификация')
        return redirect(url_for('index'))


@app.route('/2fa/generate')
def generate():
    if session.get('loggedin'):
        if gr.add_secret_key_to_user(session.get('username'), pyotp.random_base32()):
            flash('Ключ сгенерирован')
        else:
            flash('Ключ уже имеется')
        return redirect(url_for('fa'))
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('driverid', None)
    return redirect(url_for('index'))


@app.route("/cars", methods=['GET', 'POST'])
def cars():
    form = forms.CarForm()
    if form.validate_on_submit() and session.get('role') == gr.ROLE_SUPERVISOR:
        if not gr.add_car(form.brand.data, form.model.data, form.plate.data, form.year.data):
            flash('Введите уникальный госномер')
        return redirect(url_for("cars"))
    else:
        flash_errors(form)
    return render_template('cars.html', title="Автомобили", cars=gr.get_cars(), form=form)


@app.route("/cars/<int:carid>")
def car(carid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        return render_template('car.html', title="Автомобиль", car=gr.get_car(carid)[0],
                               drivers=gr.get_drivers_of_car(carid))
    else:
        return redirect(url_for('cars'))


@app.route("/cars/rm/<int:carid>")
def cars_rm(carid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if carid:
            gr.remove_car(carid)
    return redirect(url_for("cars"))


@app.route("/drivers", methods=['GET', 'POST'])
def drivers():
    form = forms.DriverForm()
    form.car.choices = gr.select_cars()
    if form.validate_on_submit():
        if gr.add_driver(form.username.data, hashlib.md5(form.password.data.encode('UTF-8')).hexdigest(), form.fio.data, form.car.data):
            app.logger.warning(f'Driver "{form.username.data}" was added by {session.get("username")}')
        else:
            flash('Пользователь уже существует')
        return redirect(url_for("drivers"))
    return render_template('drivers.html', title="Водители", drivers=gr.get_drivers(), form=form)


@app.route("/drivers/<int:driverid>")
def driver(driverid):
    if session.get('role') == gr.ROLE_SUPERVISOR or session.get('id') == driverid:
        return render_template('driver.html', title="Водитель", cars=gr.get_cars(), driver=gr.get_driver(driverid)[0],
                               transportations=gr.get_driver_transportations(driverid))
    else:
        return redirect(url_for('drivers'))


@app.route("/drivers/edit", methods=['POST'])
def drivers_edit():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if request.form['name'] and request.form.get('carid'):
            gr.edit_driver(int(request.form['driverid']), request.form['name'], int(request.form['carid']))
            flash('Автомобиль изменен')
    return redirect(url_for("driver", driverid=request.form['driverid']))


@app.route("/drivers/rm/<int:driverid>")
def drivers_remove(driverid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if driverid:
            gr.remove_driver(driverid)
    return redirect(url_for("drivers"))


@app.route("/gases", methods=['GET', 'POST'])
def gases():
    form = forms.GasForm()
    add_form = forms.GasAddForm()
    add_form.gas.choices = gr.select_gases()
    if form.validate_on_submit() and session.get('role') == gr.ROLE_SUPERVISOR:
        gr.add_gas(form.brand.data, form.octane.data)
        return redirect(url_for("gases"))
    return render_template('gases.html', title="Топливо", gases=gr.get_gases(), form=form, add_form=add_form)


@app.route("/gases/add_amount", methods=['POST'])
def gases_add_amount():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        add_form = forms.GasAddForm()
        add_form.gas.choices = gr.select_gases()
        if add_form.validate_on_submit():
            gr.add_gas_amount(int(add_form.gas.data), int(add_form.amount.data))
        else:
            flash('Заполните форму')
    return redirect(url_for("gases"))


@app.route("/gases/rm/<int:gasid>")
def gases_remove(gasid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if gasid:
            gr.remove_gas(gasid)
    return redirect(url_for("gases"))


@app.route("/stations", methods=['GET', 'POST'])
def stations():
    form = forms.StationForm()
    if form.validate_on_submit() and session.get('role') == gr.ROLE_SUPERVISOR:
        gr.add_station(form.name.data, form.address.data)
        return redirect(url_for("stations"))
    return render_template('stations.html', title="Станции", stations=gr.get_stations(), form=form)


@app.route("/stations/<int:stationid>")
def station(stationid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        return render_template('station.html', title="Станция", station=gr.get_station(stationid)[0],
                               transportations=gr.get_station_transportations(stationid))
    else:
        return redirect(url_for('stations'))


@app.route("/stations/rm/<int:stationid>")
def stations_remove(stationid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if stationid:
            gr.remove_station(stationid)
    return redirect(url_for("stations"))


@app.route("/transportations", methods=['GET', 'POST'])
def transportations():
    form = forms.TransportationForm()
    form.driver.choices = gr.select_drivers()
    form.gas.choices = gr.select_gases()
    form.station.choices = gr.select_stations()

    filter_form = forms.FilterForm()
    filter_form.driver2.choices = [("", "---")] + gr.select_drivers()
    filter_form.status.choices = [("", "---")] + gr.select_statuses()

    if filter_form.validate_on_submit():
        s = filter_form.start_date.data
        e = filter_form.end_date.data
        d = filter_form.driver2.data
        v = filter_form.status.data
        return render_template('transportations.html', title="Перевозки", transportations=gr.get_tr_sorted(s, e, d, v), form=form, filter_form=filter_form)

    if form.validate_on_submit() and session.get('role') == gr.ROLE_SUPERVISOR:
        if gr.check_tr_date(form.driver.data, form.date.data):
            if gr.add_transportation(datetime=form.date.data, driverid=int(form.driver.data), gasid=int(form.gas.data), stationid=int(form.station.data), amount=int(form.amount.data)):
                app.logger.warning(f'New transportation was added by {session.get("username")}')
            else:
                flash('Недостаточно топлива')
        else:
            flash('Время уже занято')
        return redirect(url_for('transportations'))
    else:
        flash_errors(form)
    return render_template('transportations.html', title="Перевозки", transportations=gr.get_trs(), form=form, filter_form=filter_form)


@app.route("/transportations/<int:transportationid>")
def transportation(transportationid):
    tr = gr.get_tr(transportationid)
    if session.get('role') == gr.ROLE_SUPERVISOR or session.get('id') == tr[2]:
        return render_template('transportation.html', title="Перевозка", transportation=tr, vars=gr.get_vars())
    else:
        return redirect(url_for('transportations'))


@app.route("/transportations/edit", methods=['POST'])
def transportations_edit():
    if session.get('role') >= gr.ROLE_DRIVER:
        id = request.form['trid']
        st = request.form['status']
        if id and st:
            gr.edit_tr_status(int(id), int(st))
            flash('Статус изменен')
            app.logger.warning(f'Transportation id {id} was changed to "{gr.get_var(st)[0][0]}" by {session.get("username")}')  # Добавление записи в логгер
        return redirect(url_for("transportation", transportationid=request.form['trid']))
    else:
        return redirect(url_for('transportations'))


@app.route("/transportations/rm/<int:transportationid>")
def transportations_remove(transportationid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if transportationid:
            gr.delete_transportation(transportationid)
    return redirect(url_for("transportations"))


@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/favicon.ico')
@app.route('/style.css')
@app.route('/qrcode.js')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
