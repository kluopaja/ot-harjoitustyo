import sqlite3
import sys
import logging

class DatabaseError(Exception):
    pass

def get_database_connection(database_path):
    try:
        connection = sqlite3.connect(str(database_path))
        connection.row_factory = sqlite3.Row
        return connection
    except Exception:
        logging.critical("Failed to open the database connection. "
                         "Make sure the configured database_path "
                         "is either a sqlite3 database "
                         "or a non-existing file in a valid directory")
        sys.exit()
