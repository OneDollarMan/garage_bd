import hashlib

from flask import url_for, render_template, request, redirect, send_from_directory, flash, session
from __init__ import app
import forms
import repo

gr = repo.GarageRepo(host=app.config['HOST'], user=app.config['USER'], password=app.config['PASSWORD'], db=app.config['DB'])


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
            flash('Вы авторизовались!')
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('driverid', None)
    return redirect(url_for('index'))


@app.route("/cars")
def cars():
    return render_template('cars.html', title="Автомобили", cars=gr.get_cars())


@app.route("/cars/<int:carid>")
def car(carid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        return render_template('car.html', title="Автомобиль", car=gr.get_car(carid)[0],
                               drivers=gr.get_drivers_of_car(carid))
    else:
        return redirect(url_for('cars'))


@app.route("/cars/add", methods=['POST'])
def cars_add():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if request.form['brand'] and request.form['model'] and request.form['year'] and request.form['plate']:
            if request.form['year'] <= '2022':
                gr.add_car(request.form['brand'], request.form['model'], request.form['plate'], request.form['year'])
            else:
                flash("Введите корректный год")
        else:
            flash("Заполните форму")
    return redirect(url_for("cars"))


@app.route("/cars/rm/<int:carid>")
def cars_rm(carid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if carid:
            gr.remove_car(carid)
    return redirect(url_for("cars"))


@app.route("/drivers")
def drivers():
    return render_template('drivers.html', title="Водители", cars=gr.get_cars(), drivers=gr.get_drivers(),
                           users=gr.get_all_zero_users())


@app.route("/drivers/<int:driverid>")
def driver(driverid):
    if session.get('role') == gr.ROLE_SUPERVISOR or session.get('id') == driverid:
        return render_template('driver.html', title="Водитель", cars=gr.get_cars(), driver=gr.get_driver(driverid)[0],
                               transportations=gr.get_driver_transportations(driverid))
    else:
        return redirect(url_for('drivers'))


@app.route("/drivers/add", methods=['POST'])
def drivers_add():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        u = request.form['username']
        p = request.form['password']
        f = request.form['fio']
        c = request.form.get('carid')
        if u and p and f and c:
            gr.add_driver(u, hashlib.md5(p.encode('UTF-8')).hexdigest(), f, c)
            app.logger.warning(f'Driver "{u}" was added by {session.get("username")}')
        else:
            flash('Заполните форму')
    return redirect(url_for("drivers"))


@app.route("/drivers/edit", methods=['POST'])
def drivers_edit():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if request.form['name'] and request.form['carid']:
            gr.edit_driver(int(request.form['driverid']), request.form['name'], int(request.form['carid']))
    return redirect(url_for("driver", driverid=request.form['driverid']))


@app.route("/drivers/rm/<int:driverid>")
def drivers_remove(driverid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if driverid:
            gr.remove_driver(driverid)
    return redirect(url_for("drivers"))


@app.route("/gases")
def gases():
    return render_template('gases.html', title="Топливо", gases=gr.get_gases())


@app.route("/gases/add", methods=['POST'])
def gases_add():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if request.form['octane'] and request.form['brand']:
            gr.add_gas(request.form['brand'], request.form['octane'])
        else:
            flash('Заполните форму')
    return redirect(url_for("gases"))


@app.route("/gases/add_amount", methods=['POST'])
def gases_add_amount():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if request.form.get('gasid') and request.form['amount']:
            gr.add_gas_amount(int(request.form['gasid']), int(request.form['amount']))
        else:
            flash('Заполните форму')
    return redirect(url_for("gases"))


@app.route("/gases/rm/<int:gasid>")
def gases_remove(gasid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if gasid:
            gr.rm_gas(gasid)
    return redirect(url_for("gases"))


@app.route("/stations")
def stations():
    return render_template('stations.html', title="Станции", stations=gr.get_stations())


@app.route("/stations/<int:stationid>")
def station(stationid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        return render_template('station.html', title="Станция", station=gr.get_station(stationid)[0],
                               transportations=gr.get_station_transportations(stationid))
    else:
        return redirect(url_for('stations'))


@app.route("/stations/add", methods=['POST'])
def stations_add():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if request.form['name'] and request.form['address']:
            gr.add_station(request.form['name'], request.form['address'])
        else:
            flash('Заполните форму')
    return redirect(url_for("stations"))


@app.route("/stations/rm/<int:stationid>")
def stations_remove(stationid):
    if session.get('role') == gr.ROLE_SUPERVISOR:
        if stationid:
            gr.rm_station(stationid)
    return redirect(url_for("stations"))


@app.route("/transportations")
def transportations():
    return render_template('transportations.html', title="Перевозки", transportations=gr.get_trs(),
                           gases=gr.get_gases(), drivers=gr.get_drivers(), stations=gr.get_stations())


@app.route("/transportations/<int:transportationid>")
def transportation(transportationid):
    tr = gr.get_tr(transportationid)
    if session.get('role') == gr.ROLE_SUPERVISOR or session.get('id') == tr[2]:
        return render_template('transportation.html', title="Перевозка", transportation=tr, vars=gr.get_vars())
    else:
        return redirect(url_for('transportations'))


@app.route("/transportations/add", methods=['POST'])
def transportations_add():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        dt = request.form.get('datetime')
        d = request.form.get('driverid')
        g = request.form.get('gasid')
        s = request.form.get('stationid')
        a = request.form['amount']
        if dt and d and g and s and a:
            gr.add_transportation(datetime=dt, driverid=int(d), gasid=int(g), stationid=int(s), amount=int(a))
            app.logger.warning(f'New transportation was added by {session.get("username")}')
        else:
            flash('Заполните форму')
    return redirect(url_for("transportations"))


@app.route("/transportations/edit", methods=['POST'])
def transportations_edit():
    if session.get('role') == gr.ROLE_DRIVER:
        id = request.form['trid']
        st = request.form['status']
        if id and st:
            gr.edit_tr_status(int(id), int(st))
            app.logger.warning(f'Transportation id {id} was changed to "{gr.get_var(st)[0][0]}" by {session.get("username")}')
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
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
