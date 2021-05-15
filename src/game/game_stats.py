import logging
import sys
import pandas as pd

from utils.timing import Clock, sleep_wait
from graphics.plotter import Plotter
from graphics.stats_rendering import DataFrameRenderer, ResultsRenderer
from graphics.stats_rendering import HighScoreRenderer

from database_connection import DatabaseError

class UserRecorder:
    def __init__(self, user, timer):
        self.user = user
        self._timer = timer
        self.scores = []
        self._score_sum = 0
        self.shots_fired = []
        self.kills = []
        self.deaths = []

    def total_score(self):
        return self._score_sum

    def add_score(self, value):
        self.scores.append((self._timer.current_time(), value))
        self._score_sum += value

    def add_shot(self):
        self.shots_fired.append(self._timer.current_time())

    def add_kill(self):
        self.kills.append(self._timer.current_time())

    def add_death(self):
        self.deaths.append(self._timer.current_time())

    def record_end_time(self):
        return self._timer.current_time()

    def update(self, delta_time):
        self._timer.update(delta_time)


class UserRound:
    """A class for storing some key user round statistics"""
    def __init__(self, user, score, shots, kills, deaths):
        self.user = user
        self.score = score
        self.shots = shots
        self.kills = kills
        self.deaths = deaths

    @classmethod
    def from_user_recorder(cls, user_recorder):
        """Construct UserRoundStats object from a UserRecorder object."""
        return cls(
            user = user_recorder.user,
            score = user_recorder.total_score(),
            shots = len(user_recorder.shots_fired),
            kills = len(user_recorder.kills),
            deaths = len(user_recorder.deaths)
        )

class RoundStats:
    """Class for storing statistics for a single round"""
    def __init__(self, user_recorders):
        if len(user_recorders) == 0:
            raise ValueError("At least one UserRecorder must be provided")
        self._recorders = user_recorders

    def get_round_length(self):
        """Returns the round length in seconds"""

        return self._recorders[0].record_end_time()

    def get_user_rounds(self):
        """Returns a list of UserRound objects."""
        stats_list = []
        for user_recorder in self._recorders:
            stats_list.append(UserRound.from_user_recorder(user_recorder))
        return stats_list

    def get_summary_table(self):
        """Constructs a dataframe containing the summary results.

        The dataframe will be sorted descending by the score."""
        user_rounds = sorted(self.get_user_rounds(), key=lambda x: -x.score)
        columns = {'name': [], 'score': [],
                   'shots_fired': [], 'kills': [], 'deaths': []}
        for user_round in user_rounds:
            columns['name'].append(user_round.user.name)
            columns['score'].append(user_round.score)
            columns['shots_fired'].append(user_round.shots)
            columns['kills'].append(user_round.kills)
            columns['deaths'].append(user_round.deaths)

        df = pd.DataFrame(columns)
        df['k/d'] = df['kills'] / df['deaths']
        df['shots/kills'] = df['shots_fired'] / df['kills']
        return df

    def get_verbose_table(self):
        columns = {'name': [], 'score_time': [], 'score_value': [],
                   'shot_time': [], 'kill_time': [], 'death_time': []}

        for user_recorder in self._recorders:
            max_len = max(len(user_recorder.scores), len(user_recorder.shots_fired))
            max_len = max(max_len, len(user_recorder.kills))
            max_len = max(max_len, len(user_recorder.deaths))
            for i in range(max_len):
                columns['name'].append(user_recorder.user.name)
                if i < len(user_recorder.scores):
                    columns['score_time'].append(user_recorder.scores[i][0])
                    columns['score_value'].append(user_recorder.scores[i][1])
                else:
                    columns['score_time'].append(None)
                    columns['score_value'].append(None)

                if i < len(user_recorder.shots_fired):
                    columns['shot_time'].append(user_recorder.shots_fired[i])
                else:
                    columns['shot_time'].append(None)

                if i < len(user_recorder.kills):
                    columns['kill_time'].append(user_recorder.kills[i])
                else:
                    columns['kill_time'].append(None)

                if i < len(user_recorder.deaths):
                    columns['death_time'].append(user_recorder.deaths[i])
                else:
                    columns['death_time'].append(None)


        df = pd.DataFrame(columns)
        return df

def create_results_viewer(menu_input, screen):
    dataframe_renderer = DataFrameRenderer(
        cell_size=(0.22, 0.05),
        font_color=(50, 69, 63),
        max_cell_text_length=10
    )

    plotter = Plotter()
    results_renderer = ResultsRenderer(screen, dataframe_renderer, plotter)

    return ResultsViewer(menu_input, results_renderer, Clock(2, sleep_wait))

class StatsViewer:
    def __init__(self, menu_input, clock):
        self._menu_input = menu_input
        self._clock = clock
        self._should_quit = False

    def _run(self, render_function):
        self._menu_input.clear_bindings()
        self._menu_input.bind_quit(self._quit)
        self._should_quit = False
        while not self._should_quit:
            self._menu_input.handle_inputs()
            render_function()
            self._clock.tick()

    def _quit(self):
        self._should_quit = True

class ResultsViewer(StatsViewer):
    """A class for showing the results view after the game round"""
    def __init__(self, menu_input, results_renderer, clock):
        super().__init__(menu_input, clock)
        self._renderer = results_renderer

    def run(self, round_stats):
        summary_table = round_stats.get_summary_table()
        verbose_table = round_stats.get_verbose_table()
        round_length = round_stats.get_round_length()
        self._run(
            lambda : self._renderer.render(summary_table, verbose_table,
                                           round_length)
        )


class UserStats:
    """A class for storing the user's statistics collected over many rounds"""
    def __init__(self, user, score, shots, kills, deaths, rounds):
        self.user = user
        self.score = score
        self.shots = shots
        self.kills = kills
        self.deaths = deaths
        self.rounds = rounds

class TotalStats:
    """A class for storing the statistics collected over many rounds"""
    def __init__(self, user_stats_list):
        self._user_stats_list = sorted(user_stats_list, key=lambda x: -x.score)

    def get_summary_table(self):
        """Constructs a dataframe containing the key statistics.

        The dataframe will be sorted on descending total score."""
        columns = {'name': [], 'total score': [],
                   'rounds': [], 'kills': [], 'deaths': []}
        for user_stats in self._user_stats_list:
            columns['name'].append(user_stats.user.name)
            columns['total score'].append(user_stats.score)
            columns['rounds'].append(user_stats.rounds)
            columns['kills'].append(user_stats.kills)
            columns['deaths'].append(user_stats.deaths)

        df = pd.DataFrame(columns)
        df['k/d'] = df['kills'] / df['deaths']
        return df

def create_high_score_viewer(stats_dao, n_top_players, menu_input, screen):
    dataframe_renderer = DataFrameRenderer(
        cell_size=(0.22, 0.05),
        font_color=(50, 69, 63),
        max_cell_text_length=10
    )

    high_score_renderer = HighScoreRenderer(screen, dataframe_renderer)

    return HighScoreViewer(
        stats_dao, n_top_players, menu_input, high_score_renderer,
        Clock(2, sleep_wait))

class HighScoreViewer(StatsViewer):
    """A class for viewing high scores"""
    def __init__(self, stats_dao, n_top_players, menu_input, high_score_renderer, clock):
        super().__init__(menu_input, clock)
        self._stats_dao = stats_dao
        self._n_top_players = n_top_players
        self._renderer = high_score_renderer

    def run(self):
        """Queries high scores from the database and shows them"""
        try:
            total_stats = self._stats_dao.get_top_scorers(self._n_top_players)
        except DatabaseError:
            logging.critical("Failed reading high scores from the database"
                             "Try reinitializing the database.")
            sys.exit()
        summary_table = total_stats.get_summary_table()
        self._run(lambda : self._renderer.render(summary_table))
