from database_connection import get_database_connection

def drop_tables(connection):
    cursor = connection.cursor()
    cursor.execute("drop table if exists Users")
    connection.commit()

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE Users (id INTEGER PRIMARY KEY, name TEXT UNIQUE)
    """)
    connection.commit()

def init_database():
    connection = get_database_connection()

    drop_tables(connection)
    create_tables(connection)

if __name__ == '__main__':
    init_database()
