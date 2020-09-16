import mysql.connector
import configparser


def return_database_handler():
    config = configparser.ConfigParser()
    config.read('src/tasks/config/database.ini')

    db = mysql.connector.connect(
      host=config.get('mysql', 'hostname'),
      user=config.get('mysql', 'username'),
      password=config.get('mysql', 'password'),
      database=config.get('mysql', 'database'),
    )
    return db
