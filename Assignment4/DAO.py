import DTO
import sqlite3


class Logistics:
    def __init__(self, dbcon):
        self._dbcon = dbcon

    def insert(self, logistic):  # insert Logistic DTO
        self._dbcon.execute("""
            INSERT INTO logistics (id, name, count_sent, count_received) VALUES (?, ?, ?, ?)
        """, [logistic.id, logistic.name, logistic.count_sent, logistic.count_received])

    def find(self, logistic):  # retrieve Logistic DTO
        c = self._dbcon.cursor()
        c.execute("""
            SELECT id, name FROM logistics WHERE id = ?
        """, [logistic])
        return DTO.Logistic(*c.fetchone())

    def update_count_received(self, supplier_name, quantity):
        self._dbcon.execute("""
        UPDATE logistics SET count_received = count_received + ? WHERE name = ?
        """, [quantity, supplier_name])

    def update_log_sent(self, amount, log_id):
        self._dbcon.execute("""
            UPDATE logistics
            SET count_sent = count_sent + ? WHERE id = ?""", [amount, log_id])


class Clinics:
    def __init__(self, dbcon):
        self._dbcon = dbcon

    def insert(self, clinic):
        self._dbcon.execute("""
               INSERT INTO clinics (id, location, demand, logistic) VALUES (?, ?, ?, ?)
           """, [clinic.id, clinic.location, clinic.demand, clinic.logistic])

    def find(self, clinic_id):
        c = self._dbcon.cursor()
        c.execute("""
            SELECT id, name FROM clinics WHERE id = ?
        """, [clinic_id])

        return DTO.Clinics(*c.fetchone())

    def sub_demand(self, location, amount_received):
        self._dbcon.execute("""
                UPDATE clinics SET demand = demand - ? WHERE location = ?
                """, [amount_received, location])

    def find_log(self, location):
        c = self._dbcon.cursor()
        c.execute("""
            SELECT logistic FROM clinics WHERE location = ?
        """, [location])

        return c.fetchone()[0]

class Suppliers:
    def __init__(self, dbcon):
        self._dbcon = dbcon

    def insert(self, supplier):
        self._dbcon.execute("""
            INSERT INTO suppliers (id, name, logistic) VALUES (?, ?, ?)
        """, [supplier.id, supplier.name, supplier.logistic])

    def find(self, name):
        c = self._dbcon.cursor()
        c.execute("""
            SELECT id FROM suppliers WHERE name = ?""", [name])

        return c.fetchone()[0]


class Vaccines:
    counter = 1

    def __init__(self, dbcon):
        self._dbcon = dbcon

    def insert(self, vaccine):
        self._dbcon.execute("""
        INSERT INTO vaccines (id, date, supplier, quantity) Values (?, ?, ?, ?)""",
                            [vaccine.id, vaccine.date, vaccine.supplier, vaccine.quantity])
        Vaccines.counter += 1

    def find(self, vaccine_id):
        c = self._dbcon.cursor()
        c.execute("""
                    SELECT * FROM vaccines WHERE id = ?""", [vaccine_id])
        return DTO.Vaccines(*c.fetchone())

    def delete_line(self, id_row):
        c = self._dbcon.cursor()
        c.execute("""DELETE FROM vaccines WHERE id = ?""", [id_row])

    def update_vaccine(self, id_row, amount):
        self._dbcon.execute("""UPDATE vaccines SET quantity = quantity - ? WHERE id = ?""", [amount, id_row])

