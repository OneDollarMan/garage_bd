import datetime

from mysql.connector import connect, Error


class GarageRepo:
    ROLE_DRIVER = 1
    ROLE_SUPERVISOR = 2

    def __init__(self, host, user, password, db):  # Конструктор класса
        self.connection = None
        self.cursor = None
        self.connect_to_db(host, user, password, db)
        if self.connection is not None and self.cursor is not None:
            self.select_db(db)

            self.get_tables = lambda: self.raw_query("SHOW TABLES")  # Лямбды это запросы к бд

            self.get_user = lambda username: self.raw_query(
                "SELECT * FROM user WHERE username='%s' AND role != '0'" % username)
            self.login_user = lambda username, password: self.get_query(
                """SELECT * FROM user WHERE username=%(u)s AND password=%(p)s""", args={'u': username, 'p': password})

            self.insert_car = lambda brand, model, plate, year: self.write_query(
                "INSERT INTO car SET brand='%s', model='%s', plate='%s', year=%d" % (
                    brand, model, plate, int(year)))
            self.get_cars = lambda: self.raw_query("SELECT * FROM garage.car")
            self.rm_car = lambda idcar: self.write_query("DELETE FROM car WHERE idcar=%d" % int(idcar))
            self.get_car = lambda idcar: self.raw_query("SELECT * FROM car WHERE idcar = %d LIMIT 1" % idcar)
            self.get_car_by_plate = lambda plate: self.raw_query(f"SELECT * FROM car WHERE plate='{plate}'")
            self.select_cars = lambda: self.raw_query("SELECT idcar, CONCAT(brand, ' ', model, ' ', plate) FROM car")

            self.get_driver = lambda driverid: self.raw_query(
                "SELECT * FROM user LEFT JOIN car ON user.car = car.idcar WHERE iduser = %d" % driverid)
            self.get_drivers = lambda: self.raw_query(
                "SELECT * FROM user LEFT JOIN car ON user.car = car.idcar WHERE user.role=1")
            self.reg_driver = lambda u, p, fio, carid: self.write_query(
                f"INSERT INTO user SET username='{u}', password='{p}', fio='{fio}', role=1, car=(SELECT idcar FROM car WHERE idcar = '{carid}')")
            self.get_drivers_of_car = lambda carid: self.raw_query("SELECT * FROM user WHERE car = %d" % carid)
            self.remove_driver = lambda iddriver: self.write_query(
                "UPDATE user SET role=0, car=0 WHERE iduser=%d" % int(iddriver))
            self.edit_driver = lambda driverid, name, carid: self.write_query(
                "UPDATE user SET fio = '%s', car = %d WHERE iduser = %d" % (name, carid, driverid))
            self.get_driver_transportations = lambda driverid: self.raw_query(
                "SELECT * FROM transportation JOIN var ON status=var.idvar WHERE driver = %d" % driverid)
            self.select_drivers = lambda: self.raw_query("SELECT iduser, fio FROM user WHERE role=1")

            self.get_gases = lambda: self.raw_query("SELECT * FROM garage.gas")
            self.add_gas = lambda brand, octane: self.write_query(
                "INSERT INTO gas SET brand='%s', octane='%d'" % (brand, int(octane)))
            self.rm_gas = lambda gasid: self.write_query("DELETE FROM gas WHERE idgas='%d'" % gasid)
            self.add_gas_amount = lambda gasid, amount: self.write_query(
                "UPDATE gas SET remain = remain + %d WHERE idgas = %d AND remain + %d > remain" % (
                    amount, gasid, amount))
            self.change_gas_amount = lambda gasid, amount: self.write_query(
                "UPDATE gas SET remain = remain + %d WHERE idgas = %d" % (amount, gasid))
            self.select_gases = lambda: self.raw_query("SELECT idgas, CONCAT(brand, ' ', octane) FROM gas")

            self.get_stations = lambda: self.raw_query("SELECT * FROM station")
            self.get_station = lambda stationid: self.raw_query("SELECT * FROM station WHERE idstation=%d" % stationid)
            self.add_station = lambda name, address: self.write_query(
                "INSERT INTO station SET name='%s', address='%s'" % (name, address))
            self.rm_station = lambda stationid: self.write_query("DELETE FROM station WHERE idstation='%d'" % stationid)
            self.get_station_transportations = lambda stationid: self.raw_query(
                "SELECT * FROM transportation WHERE station = %d" % stationid)
            self.select_stations = lambda: self.raw_query(
                "SELECT idstation, CONCAT(name, ' (', address, ')') FROM station")

            self.add_tr = lambda datetime, driverid, gasid, stationid, amount: self.write_query(
                "INSERT INTO transportation SET date='%s', driver='%d', gas=%d, station=%d, gas_amount=%d" %
                (datetime, driverid, gasid, stationid, amount))
            self.get_trs = lambda: self.get_double_list_query(
                "SELECT * FROM transportation JOIN user, gas, station, var WHERE driver=iduser AND gas=idgas AND station=idstation AND status=idvar")
            self.get_tr = lambda trid: self.get_one_list_query(
                "SELECT * FROM transportation JOIN user, gas, station, var WHERE idtransportation=%d AND driver=iduser AND gas=idgas AND station=idstation AND status=idvar" % trid)
            self.edit_tr_status = lambda trid, status: self.raw_query(
                "UPDATE transportation SET status=%d WHERE idtransportation=%d" % (status, trid))
            self.rm_tr = lambda id: self.write_query(f"DELETE FROM transportation WHERE idtransportation='{id}'")

            self.select_statuses = lambda: self.raw_query("SELECT idvar, text FROM var")

            self.get_vars = lambda: self.raw_query("SELECT * FROM var")
            self.get_var = lambda id: self.raw_query(f"SELECT text FROM var WHERE idvar='{id}'")
            self.get_cars_count = lambda: self.get_one_query("SELECT COUNT(1) FROM garage.car")
            self.get_users_count = lambda: self.get_one_query("SELECT COUNT(1) FROM garage.user WHERE role=1")
            self.get_gases_count = lambda: self.get_one_query("SELECT COUNT(1) FROM garage.gas")
            self.get_stations_count = lambda: self.get_one_query("SELECT COUNT(1) FROM garage.station")
            self.get_transportations_count = lambda: self.get_one_query("SELECT COUNT(1) FROM garage.transportation t JOIN user u ON t.driver=u.iduser WHERE gas != 0 AND station != 0 AND (role != 0 OR status > 0)")
        else:
            print('connection failed')

    def connect_to_db(self, host, user, password, db):  # Подключение к бд и загрузка дампа
        try:
            self.connection = connect(host=host, user=user, password=password)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SHOW DATABASES")
            for res in self.cursor:
                if res[0] == db:
                    self.cursor.fetchall()
                    return
            for line in open('dump.sql'):
                self.cursor.execute(line)
            self.connection.commit()
            print('dump loaded successfully')
        except Error as e:
            print(e)

    def select_db(self, db):
        self.cursor.execute(f"USE {db}")

    def raw_query(self, query):  # Функция выполнения запроса к бд
        if self.cursor and query:
            self.cursor.execute(query)
            return self.cursor.fetchall()

    def write_query(self, query):  # Функция записи данных в бд
        if self.cursor and query:
            self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.fetchall()

    def get_one_query(self, query):  # Ниже то же самое, отличие в выводе результата
        if self.cursor and query:
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]

    def get_query(self, query, args):
        if self.cursor and query:
            self.cursor.execute(query, args)
            return self.cursor.fetchone()

    def get_one_list_query(self, query):
        if self.cursor and query:
            self.cursor.execute(query)
            return [*self.cursor.fetchall()[0]]

    def get_double_list_query(self, query):
        if self.cursor and query:
            self.cursor.execute(query)
            return [[it for it in item] for item in self.cursor.fetchall()]

    def add_car(self, brand, model, plate, year):  # Добавление авто
        plate = plate.upper()
        if not self.get_car_by_plate(plate):
            self.insert_car(brand, model, plate, year)
            return True
        return False

    def remove_car(self, carid):  # Удаление авто
        if carid:
            self.write_query("UPDATE user SET car = NULL WHERE car = %d" % carid)
            self.rm_car(carid)

    def remove_station(self, id):
        self.rm_station(id)
        ids = self.raw_query(f"SELECT idtransportation FROM transportation WHERE station='{id}'")
        for i in ids:
            self.delete_transportation(i[0])

    def remove_gas(self, id):
        self.rm_gas(id)
        self.write_query(f"UPDATE transportation SET gas='0' WHERE gas='{id}'")

    def check_tr_date(self, id, new_date):  # Проверка даты транспортировки при добавлении
        q = self.raw_query(
            f"SELECT date FROM transportation JOIN user ON transportation.driver=user.iduser WHERE car=(SELECT car FROM user WHERE iduser={id}) AND gas != 0 AND station != 0")
        for date in q:
            print(new_date, date[0], (new_date - date[0]).total_seconds())
            if abs((new_date - date[0]).total_seconds()) < 3600:
                return False
        return True

    def add_transportation(self, gasid, amount, datetime, driverid, stationid):  # Добавление транспортировки
        q = self.get_one_query("SELECT remain FROM gas WHERE idgas=%d" % gasid)
        if q >= amount:
            self.add_tr(datetime, driverid, gasid, stationid, amount)
            self.change_gas_amount(gasid=gasid, amount=-amount)
            return True
        else:
            return False

    def add_driver(self, username, password, fio, carid):  # Добавление водителя
        if not self.get_user(username):
            self.reg_driver(username, password, fio, carid)
            return True
        else:
            return False

    def delete_transportation(self, transportationid):  # Удаление транспортировки
        if transportationid:
            amount = self.get_query(f"SELECT gas, gas_amount FROM transportation WHERE idtransportation='%(id)s'",
                                    args={'id': transportationid})
            self.change_gas_amount(gasid=amount[0], amount=amount[1])
            self.rm_tr(transportationid)

    def get_tr_sorted(self, start_date, end_date, driver, status):
        q = "SELECT * FROM transportation JOIN user, gas, station, var WHERE driver=iduser AND gas=idgas AND station=idstation AND status=idvar"
        if start_date:
            q = q + " AND date > '%s'" % start_date
        if end_date:
            q = q + " AND date < '%s'" % end_date
        if driver:
            q = q + " AND driver = '%d'" % int(driver)
        if status:
            q = q + " AND status = '%d'" % int(status)
        return self.raw_query(q)
