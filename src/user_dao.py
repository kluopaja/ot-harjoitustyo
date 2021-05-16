from database_connection import DatabaseError
from user import User
class UserDao:
    """Class for User related database queries"""
    def __init__(self, connection):
        """Initializes UserDao

        Arguments:
            `connection`: sqlite3.Connection
        """
        self._connection = connection
        self._cursor = self._connection.cursor()

    def get_by_name(self, name):
        """Returns the user with name `name` or None if no such user exists."""
        try:
            self._cursor.execute("SELECT * from Users WHERE name=?", (name,))
            result = self._cursor.fetchone()
            return self._row_to_user(result)
        except Exception:
            raise DatabaseError


    def get_first(self):
        """Returns the user with the lexicographically smallest name.

        Returns:
            User or None if no suitable User was found """
        try:
            self._cursor.execute("SELECT * from Users ORDER BY name LIMIT 1")
            result = self._cursor.fetchone()
            if result is None:
                return None

            return self._row_to_user(result)
        except Exception:
            raise DatabaseError

    def get_next(self, user):
        """Returns the User after `user` in lexicographical order by name"""
        try:
            self._cursor.execute(
                "SELECT * from Users WHERE name > ? ORDER BY name LIMIT 1",
                (user.name,)
            )
            result = self._cursor.fetchone()
            return self._row_to_user(result)
        except Exception:
            raise DatabaseError

    def get_previous(self, user):
        """Returns the User after `user` in lexicographical order by name"""
        try:
            self._cursor.execute(
                "SELECT * from Users WHERE name < ? ORDER BY name DESC LIMIT 1",
                (user.name,)
            )
            result = self._cursor.fetchone()
            return self._row_to_user(result)
        except Exception:
            raise DatabaseError

    def create(self, user):
        """Creates a new user to the database.

        Arguments:
            `user`: User
                The user to be created to the database
                `user.id` should be None
        """


        if user.id is not None:
            raise ValueError("`user.id` should be None")

        try:
            self._cursor.execute(
                "INSERT INTO Users (name) VALUES (?)",
                (user.name,)
            )
            self._connection.commit()
        except Exception:
            raise DatabaseError

    def _row_to_user(self, row):
        if row is None:
            return None
        user = User(row['name'])
        user.id = row['id']
        return user
