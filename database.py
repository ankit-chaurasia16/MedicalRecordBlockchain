import os
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "medical_app"),
    "password": os.getenv("MYSQL_PASSWORD", "MedicalApp@2026"),
    "database": os.getenv("MYSQL_DATABASE", "medical_blockchain")
}

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as error:
        print("MySQL connection error:", error)
        raise
