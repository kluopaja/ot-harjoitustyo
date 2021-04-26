from user import User
class UserDao:
    def __init__(self, connection):
        self._connection = connection
        self._cursor = self._connection.cursor()

    def get_by_name(self, name):
        """Returns the user with name `name` or None if no such user exists."""
        self._cursor.execute("SELECT * from Users WHERE name=?", (name,))
        result = self._cursor.fetchone()
        return self._row_to_user(result)

    def get_first(self):
        """Returns the user with the lexicographically smallest name."""
        self._cursor.execute("SELECT * from Users ORDER BY name LIMIT 1")
        result = self._cursor.fetchone()
        return self._row_to_user(result)

    def get_next(self, user):
        """Returns the user after `user` in lexicographical order by name"""
        self._cursor.execute(
            "SELECT * from Users WHERE name > ? ORDER BY name LIMIT 1",
            (user.name,)
        )
        result = self._cursor.fetchone()
        return self._row_to_user(result)

    def get_previous(self, user):
        """Returns the user after `user` in lexicographical order by name"""
        self._cursor.execute(
            "SELECT * from Users WHERE name < ? ORDER BY name DESC LIMIT 1",
            (user.name,)
        )
        result = self._cursor.fetchone()
        return self._row_to_user(result)

    def create(self, user):
        """Saves user `user` to the database.

        Returns:
            True if the saving was successful.
            False otherwise
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
            return False

        return True

    def update(self, user):
        """Updates user `user` in the database.

        Returns:
            True if the update was successful.
            False otherwise.
        """
        if user.id is None:
            raise ValueError("`user.id` should not be None")

        try:
            self._cursor.execute(
                "UPDATE Users SET name=? WHERE id=?",
                (user.name, user.id)
            )
        except Exception:
            return False

        return True

    def _row_to_user(self, row):
        if row is None:
            return None
        user = User(row['name'])
        user.id = row['id']
        return user
