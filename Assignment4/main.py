import atexit
import Repository
from Repository import repo

import DTO
import DAO
import os
import sys


def main(config_file, order_file, output_file):
    cursor = repo._dbcon.cursor()
    repo.create_tables()
    config = repo.read_insert(config_file)
    orders = repo.read_orders_file(order_file, output_file)

#  v, s, c, lo = Read_Parse_file.what_to_insert_to_db(Read_Parse_file, config_file)
#  # populate_db only once
#  if (repo.is_db_empty()):
#      repo.populate_db(v, s, c, lo)
#  print(config)
#
#  print(orders)
#
#  repo.orders(orders, output_file)
#
#
# # repo.drop_db_tables()


if __name__ == '__main__':
    main("config.txt", "orders.txt", "output.txt")
