import sqlite3
from config import DATABASE_PATH

connection = sqlite3.connect(str(DATABASE_PATH))
connection.row_factory = sqlite3.Row
class DatabaseError(Exception):
    pass


def get_database_connection():
    return connection
