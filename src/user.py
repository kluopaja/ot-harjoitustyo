class User:
    """A class representing a game user.

    Attributes:
        name: a string
            The name of the user
    """
    def __init__(self, name):
        self.id = None
        self.name = name


class UserFactory:
    """A class for creating a new user to the database"""
    def __init__(self, user_dao):
        self.user_dao = user_dao
        self.reset()

    def reset(self):
        """Resets the user currently being modified to the default"""
        self._user = User("User");

    def name_valid(self):
        """Checks if the current name is unique.
        
        Returns:
            True if the user's name is unique in `user_dao`.
            False otherwise.
        """
        return self.user_dao.get_by_name(self.get_name()) is None

    def create_user(self):
        """Stores the currently modified user to the database.

        Returns:
            True if the operation was successful.
            False otherwise.
        """
        return self.user_dao.create(self._user)

    def get_name(self):
        """Returns the name of the currently modified user"""
        return self._user.name

    def set_name(self, name):
        """Sets the currently modified user's name"""
        self._user.name = name

