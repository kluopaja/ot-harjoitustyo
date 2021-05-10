from database_connection import get_database_connection

def drop_tables(connection):
    cursor = connection.cursor()
    cursor.execute("drop table if exists Users")
    cursor.execute("drop table if exists RoundStats")
    connection.commit()

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = on")
    cursor.execute(
    "CREATE TABLE Users (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    cursor.execute("""
    CREATE TABLE RoundStats (
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES Users (id) ON DELETE CASCADE,
        score INTEGER NOT NULL,
        shots INTEGER,
        kills INTEGER,
        deaths INTEGER,
        CHECK(shots >= 0),
        CHECK(kills >= 0),
        CHECK(deaths >= 0)
        )
    """)
    connection.commit()

def init_database():
    connection = get_database_connection()

    drop_tables(connection)
    create_tables(connection)

if __name__ == '__main__':
    init_database()
