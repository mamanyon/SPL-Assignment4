import sqlite3
import atexit
import os

# The Repository
import DAO
import DTO

os.path.isfile('config.txt')


class Repository:
    def __init__(self):
        myfile = 'database.db'
        if os.path.isfile(myfile):
            os.remove(myfile)
        self._dbcon = sqlite3.connect('database.db')
        self.vaccines = DAO.Vaccines(self._dbcon)
        self.clinics = DAO.Clinics(self._dbcon)
        self.suppliers = DAO.Suppliers(self._dbcon)
        self.logistics = DAO.Logistics(self._dbcon)

    def read_insert(self, config_file):
        with open(config_file) as f:
            f = f.readlines()  # f stands for file -- make my file a list
        config_first_line = f[0]
        config_first_line = config_first_line[:-1]
        split_config_first_line = config_first_line.split(",")

        list_entries_vaccines = []
        list_entries_suppliers = []
        list_entries_clinics = []
        list_entries_logistics = []
        lines_to_read_vac = int(split_config_first_line[0])
        lines_to_read_sup = int(split_config_first_line[1])
        lines_to_read_clin = int(split_config_first_line[2])
        lines_to_read_log = int(split_config_first_line[3])
        range1 = range(1, 1 + lines_to_read_vac)
        range2 = range(1 + lines_to_read_vac, lines_to_read_sup + 1 + lines_to_read_vac)
        range3 = range(lines_to_read_sup + 1 + lines_to_read_vac,
                       lines_to_read_sup + 1 + lines_to_read_vac + lines_to_read_clin)
        range4 = range(lines_to_read_sup + 1 + lines_to_read_vac + lines_to_read_clin,
                       lines_to_read_sup + 1 + lines_to_read_vac + lines_to_read_clin + lines_to_read_log)

        for i in range1:
            list_entries_vaccines.append(f[i])
        for i in range2:
            list_entries_suppliers.append(f[i])
        for i in range3:
            list_entries_clinics.append(f[i])
        for i in range4:
            list_entries_logistics.append(f[i])

        for i in list_entries_vaccines:
            i = i[:-1]
            i = i.split(',')
            vaccine = DTO.Vaccines(*i)
            insert_vac = DAO.Vaccines(self._dbcon)
            insert_vac.insert(vaccine)

        for i in list_entries_suppliers:
            i = i[:-1]
            i = i.split(',')
            supplier = DTO.Suppliers(*i)
            insert_sup = DAO.Suppliers(self._dbcon)
            insert_sup.insert(supplier)

        for i in list_entries_clinics:
            i = i[:-1]
            i = i.split(',')
            clinic = DTO.Clinics(*i)
            insert_cli = DAO.Clinics(self._dbcon)
            insert_cli.insert(clinic)

        for i in list_entries_logistics:
            if i[-1] == '\n':
                i = i[:-1]
            i = i.split(',')
            logistic = DTO.Logistic(*i)
            insert_log = DAO.Logistics(self._dbcon)
            insert_log.insert(logistic)

    def read_orders_file(self, orders_file, output_file):
        file = open(output_file, "w+")
        total_received = 0
        with open(orders_file) as f:
            f = f.readlines()
            total_sent = 0;
            for i in f:
                if i[-1] == '\n':
                    i = i[:-1]
                split_orders_line = i.split(",")

                if len(split_orders_line) == 3:  # Received Shipment
                    supplier = split_orders_line[0]
                    amount = split_orders_line[1]
                    date = split_orders_line[2]
                    self.receive_shipment(supplier, amount, date)

                    # for the output file
                    total_inventory = self.get_total_inventory()
                    total_demand = self.get_total_demand()
                    int_amount = int(amount)
                    total_received = total_received + int_amount
                    line_to_add = str(total_inventory) + ',' + str(total_demand) + ',' + str(
                        total_received) + ',' + str(total_sent) + '\n'
                    file.write(line_to_add)
                else:  # Send Shipment
                    location = split_orders_line[0]
                    amount = split_orders_line[1]
                    self.send_shipment(location, int(amount))

                    # for the output file
                    total_inventory = self.get_total_inventory()
                    total_demand = self.get_total_demand()
                    int_amount = int(amount)
                    total_sent += int_amount

                    line_to_add = str(total_inventory) + ',' + str(total_demand) + ',' + str(
                        total_received) + ',' + str(total_sent) + '\n'
                    file.write(line_to_add)

    def send_shipment(self, destination, quantity_to_ship):
        DAO.Clinics.sub_demand(self.clinics, destination, quantity_to_ship)
        log = DAO.Clinics.find_log(self.clinics, destination)
        DAO.Logistics.update_log_sent(self.logistics, quantity_to_ship, log)
        cursor = self._dbcon.cursor()
        while quantity_to_ship > 0 :
            cursor.execute("""SELECT id,quantity,supplier FROM vaccines ORDER BY date ASC""")
            vaccine = cursor.fetchone()
            quantity = vaccine[1]
            gap = quantity - quantity_to_ship
            if gap < 0:
                DAO.Vaccines.delete_line(self.vaccines, vaccine[0])
            else:
                DAO.Vaccines.update_vaccine(self.vaccines, vaccine[0], quantity_to_ship)
            quantity_to_ship = quantity_to_ship - quantity

    def receive_shipment(self, name, amount, date):
        cursor = self._dbcon.cursor()
        # finding the unique id
        id = DAO.Vaccines.counter
        supp_id = DAO.Suppliers.find(self.suppliers, name)
        new_row_vaccine = DTO.Vaccines(id, date, supp_id, amount)
        DAO.Vaccines.insert(self.vaccines, new_row_vaccine)
        cursor.execute("""SELECT logistic FROM suppliers WHERE name=(?)""", [name])
        sup_logistic_id = cursor.fetchone()[0]
        self.update_count_suppliers(sup_logistic_id, int(amount))

    def _close(self):
        self._dbcon.commit()
        self._dbcon.close()

    def create_tables(self):
        self._dbcon.executescript("""
                CREATE TABLE vaccines (
                    id           INT         PRIMARY KEY,
                    date        DATE        NOT NULL,
                    supplier     INT        REFERENCES supplier(id),
                    quantity     INT           NOT NULL
                ); 

                CREATE TABLE suppliers (
                    id        INT     PRIMARY KEY,
                    name     STRING    NOT NULL,
                    logistic  INT      REFERENCES logistic(id)
                );

                CREATE TABLE clinics (
                    id      INT         PRIMARY KEY,
                    location    STRING     NOT NULL,
                    demand      INT        NOT NULL,
                    logistic    INT     REFERENCES logistic(id)
                );

                CREATE TABLE logistics (
                    id              INT     PRIMARY KEY,
                    name          STRING    NOT NULL,
                    count_sent      INT     NOT NULL,
                    count_received  INT     NOT NULL
                );
            """)

    def update_count_suppliers(self, sup_logistic_id, amount):
        cursor = self._dbcon.cursor()
        cursor.execute("""SELECT count_received FROM logistics WHERE id=(?) """, [sup_logistic_id])
        updated_amount = cursor.fetchone()[0] + amount
        cursor.execute("""UPDATE logistics  SET count_received = ?  WHERE id=(?) """, [updated_amount, sup_logistic_id])

    def get_total_inventory(self):
        cursor = self._dbcon.cursor()
        cursor.execute("""SELECT SUM(quantity) FROM vaccines""")
        return cursor.fetchone()[0]

    def get_total_demand(self):
        cursor = self._dbcon.cursor()
        cursor.execute("""SELECT SUM(demand) FROM clinics""")
        return cursor.fetchone()[0]



# the repository singleton
repo = Repository()
atexit.register(repo._close)


