from game.game_stats import UserStats, TotalStats
from user import User
from database_connection import DatabaseError
class StatsDao:
    def __init__(self, connection):
        self._connection = connection
        self._cursor = self._connection.cursor()

    def save_user_rounds(self, user_rounds):
        """Saves a list of UserRound object to the database.

        Ignores User objects with User.id == None.
        """
        try:
            for user_round in user_rounds:
                user = user_round.user
                if user.id is None:
                    continue

                self._cursor.execute(
                    """INSERT INTO
                        RoundStats (user_id, score, shots, kills, deaths)
                    VALUES
                        (?, ?, ?, ?, ?)""",
                    (user.id, user_round.score, user_round.shots,
                    user_round.kills, user_round.deaths)
                )
            self._connection.commit()
        except Exception:
            raise DatabaseError

    def get_top_scorers(self, n_players):
        """Returns a TotalStats object corresponding to the top `n_players`."""
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
