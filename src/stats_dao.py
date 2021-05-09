class StatsDao:
    def __init__(self, connection):
        self._connection = connection
        self._cursor = self._connection.cursor()

    def save_round_stats(self, round_stats):
        pass

    def get_top_scorers(self, n_players):
        pass
