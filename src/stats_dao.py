from game.game_stats import UserStats, TotalStats
from user import User
from database_connection import DatabaseError
class StatsDao:
    """A class for game statistics related database queries"""
    def __init__(self, connection):
        """Initializes StatsDao

        Arguments:
            `connection`: sqlite3.Connection
        """
        self._connection = connection
        self._cursor = self._connection.cursor()

    def save_player_rounds(self, player_rounds):
        """Saves a list of PlayerRound object to the database.

        Ignores User objects with User.id == None.

        Arguments:
            `player_rounds`: list of PlayerRound objects
        """
        try:
            for player_round in player_rounds:
                user = player_round.user
                if user.id is None:
                    continue

                self._cursor.execute(
                    """INSERT INTO
                        RoundStats (user_id, score, shots, kills, deaths)
                    VALUES
                        (?, ?, ?, ?, ?)""",
                    (user.id, player_round.score, player_round.shots,
                    player_round.kills, player_round.deaths)
                )
            self._connection.commit()
        except Exception:
            raise DatabaseError

    def get_top_scorers(self, n_players):
        """Returns a statistics for top `n_players`.

        Arguments:
            `n_players`: a non-negative integer
        Returns:
            TotalStats
                an object corresponding to the top `n_players`.
        """
        try:
            self._cursor.execute("""
            SELECT
                Users.id AS id, name, SUM(score) AS score, SUM(shots) AS shots,
                SUM(kills) AS kills, SUM(deaths) AS deaths, COUNT(Users.id) as rounds
            FROM
                RoundStats, Users
            WHERE
                RoundStats.user_id == Users.id
            GROUP BY
                Users.id
            ORDER BY
                SUM(score)
            LIMIT ?""", (n_players,))
            results = self._cursor.fetchall()
            return TotalStats([self._row_to_user_stats(row) for row in results])
        except Exception:
            raise DatabaseError

    def _row_to_user_stats(self, row):
        if row is None:
            return None
        user = User(row["name"])
        user.id = row["id"]
        return UserStats(
            user, row["score"], row["shots"], row["kills"], row["deaths"],
            row["rounds"])
