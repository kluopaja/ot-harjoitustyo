import logging
import sys
from database_connection import DatabaseError
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
        self._user = User("User")

    def name_valid(self):
        """Checks if the current name is unique.

        NOTE: Exits the program if the operation was not successful.

        Returns:
            True if the user's name is unique in `user_dao`.
            False otherwise.
        """
        try:
            user = self.user_dao.get_by_name(self.get_name())
            return user is None
        except DatabaseError:
            logging.critical("Error accessing database! "
                             "Try reinitializing the database.")
            sys.exit()


    def create_user(self):
        """Stores the currently modified user to the database.

        NOTE: Exits the program if the operation was not successful."""
        try:
            self.user_dao.create(self._user)
        except DatabaseError:
            logging.critical("Error creating a new user to the database! "
                             "Try reinitializing the database.")
            sys.exit()

    def get_name(self):
        """Returns the name of the currently modified user"""
        return self._user.name

    def set_name(self, name):
        """Sets the currently modified user's name"""
        self._user.name = name

class UserSelector:
    """A class for browsing through and selecting Users from database.

    NOTE: If the database doesn't contain any User data, then
    the class will work as if there was a single default user
    in the database."""
    def __init__(self, user_dao):
        """Initializes UserSelector.

        Arguments:
            `user_dao`: a UserDao object
        """
        self._user_dao = user_dao
        self._selected = None
        self._init_selected()

    def _init_selected(self):
        if self._selected is not None:
            return

        try:
            self._selected = self._user_dao.get_first()
        except DatabaseError:
            self._error()

    def _error(self):
        logging.critical("Failed accessing the database. "
                         "Try reinitializing the database")
        sys.exit()

    def next(self):
        """Select the next User in lexicographical order.

        Does nothing if no next User exists in the database."""
        self._init_selected()
        if self._selected is None:
            return

        try:
            next_selected = self._user_dao.get_next(self._selected)
        except DatabaseError:
            self._error()

        if next_selected is not None:
            self._selected = next_selected

    def previous(self):
        """Select the previous User in lexicographical order.

        Does nothing if no previous User exists in the database."""
        self._init_selected()
        if self._selected is None:
            return
        try:
            next_selected = self._user_dao.get_previous(self._selected)
        except DatabaseError:
            self._error()

        if next_selected is not None:
            self._selected = next_selected

    def get_current(self):
        """Returns the selected User.

        Returns:
            User object

            NOTE: If the database doesn't contain any Users, then
            returns a default user with User.id == None!
        """
        self._init_selected()
        if self._selected is None:
            return User("default user")
        return self._selected
