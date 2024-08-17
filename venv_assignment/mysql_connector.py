import mysql.connector
from mysql.connector import Error

# Task 1: Setting Up the Flask Environment and Database Connection

class MySQLConnector:
    def get_db_connection(self):
        try:
            conn = mysql.connector.connect(
database = "fitness_center_db",
user = "root",
password = "Jajoconi@1",
host = "localhost"
)
            
            return conn
        except Error as e:
            print(f"Error: {e}.")

            return False