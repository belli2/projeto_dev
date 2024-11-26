#importar o conector do MySQL
import mysql.connector

def open_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='manutencao',
        port='3309'
    )