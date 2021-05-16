import logging
import sys
import pandas as pd

from utils.timing import Clock, sleep_wait
from graphics.plotter import Plotter
from graphics.stats_rendering import DataFrameRenderer, ResultsRenderer
from graphics.stats_rendering import HighScoreRenderer

from database_connection import DatabaseError

class PlayerRecorder:
    """A class for recording the statistics of a Player associated with a User.

    NOTE: Currently is is possible for a single user to control many
    Players in a Game.

    Attributes:
        `user`: A User
            The user who is playing the Player being recorded
        `scores`: A list of tuples `(score, time)`
            The `score` is the score got at time `time`
        `shots_fired`: A list of floats
            The times at which the associated Player shot a bullet
        `kills`: A list of floats
            The times at which the associated Player killed another Player.
        `deaths`: A list of float
            The times at which the associated Player died.
        """
    def __init__(self, user, timer):
        """Initializes a PlayerRecorder.

        Arguments:
            `user`: A User
                The user who is playing the Player being recorded
            `timer`: A Timer
                The Timer for adding the time information for some events.
        """
        self.user = user
        self._timer = timer
        self.scores = []
        self._score_sum = 0
        self.shots_fired = []
        self.kills = []
        self.deaths = []

    def total_score(self):
        """Returns the total recorded score"""
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
        """Returns the last time the PlayerRecorder was active."""
        return self._timer.current_time()

    def update(self, delta_time):
        """Updates the PlayerRecorder timer."""
        self._timer.update(delta_time)


class PlayerRound:
    """A class for storing some key player round statistics.

    NOTE: Currently is is possible for a single user to control many
    Players in a Game. In this case, there can be many PlayerRound
    classes associated with the same User in a single round.

    Attributes:
        `user`: A User
            The user who is playing the Player whose stats are stored
        `score`: A float
        `shots`: An integer
            The number of shots the Player
        `kills`:
            The number of times the Player killed another Player.
        `deaths`:
            The number of time the Player died.
    """

    def __init__(self, user, score, shots, kills, deaths):
        """Initializes a PlayerRound.

        Arguments:
        `user`: A User
            The user who is playing the Player whose stats are stored
        `score`: A float
        `shots`: An integer
            The number of shots the Player
        `kills`:
            The number of times the Player killed another Player.
        `deaths`:
            The number of time the Player died.
        """

        self.user = user
        self.score = score
        self.shots = shots
        self.kills = kills
        self.deaths = deaths

    @classmethod
    def from_player_recorder(cls, player_recorder):
        """Construct PlayerRound object from a PlayerRecorder object."""
        return cls(
            user = player_recorder.user,
            score = player_recorder.total_score(),
            shots = len(player_recorder.shots_fired),
            kills = len(player_recorder.kills),
            deaths = len(player_recorder.deaths)
        )

class RoundStats:
    """Class for storing statistics for a single Game"""
    def __init__(self, player_recorders):
        """Initializes a RoundStats object.

        Arguments:
            `player_recorders`: A list of PlayerRecorder objects.
                The PlayerRecorders of the Game
        """
        if len(player_recorders) == 0:
            raise ValueError("At least one PlayerRecorder must be provided")
        self._recorders = player_recorders

    def get_round_length(self):
        """Returns the round length in seconds"""
        return self._recorders[0].record_end_time()

    def get_player_rounds(self):
        """Returns a list of PlayerRound objects."""
        stats_list = []
        for player_recorder in self._recorders:
            stats_list.append(PlayerRound.from_player_recorder(player_recorder))
        return stats_list

    def get_summary_table(self):
        """Constructs a pandas dataframe containing the summary results.

        The dataframe will be sorted descending by the score.

        Returns:
            A pandas DataFrame with columns:
                'name', 'score', 'shots_fired', 'kills', 'deaths', 'k/d',
                'shots/kills'
                sorted descending by the column 'score'"""
        player_rounds = sorted(self.get_player_rounds(), key=lambda x: -x.score)
        columns = {'name': [], 'score': [],
                   'shots_fired': [], 'kills': [], 'deaths': []}
        for player_round in player_rounds:
            columns['name'].append(player_round.user.name)
            columns['score'].append(player_round.score)
            columns['shots_fired'].append(player_round.shots)
            columns['kills'].append(player_round.kills)
            columns['deaths'].append(player_round.deaths)

        data_frame = pd.DataFrame(columns)
        data_frame['k/d'] = data_frame['kills'] / data_frame['deaths']
        data_frame['shots/kills'] = data_frame['shots_fired'] / data_frame['kills']
        return data_frame

    def get_verbose_table(self):
        """Construct a pandas dataframe containing more detailed results.

        Returns:
            A pandas DataFrame with columns:
                'name', 'score_time', 'score_value', 'shot_time',
                'kill_time', 'death_time'

                Every column will have a value in 'name' but otherwise
                the cells might be empty.
        """
        columns = {'name': [], 'score_time': [], 'score_value': [],
                   'shot_time': [], 'kill_time': [], 'death_time': []}

        for player_recorder in self._recorders:
            max_len = max(len(player_recorder.scores), len(player_recorder.shots_fired))
            max_len = max(max_len, len(player_recorder.kills))
            max_len = max(max_len, len(player_recorder.deaths))
            for i in range(max_len):
                columns['name'].append(player_recorder.user.name)
                if i < len(player_recorder.scores):
                    columns['score_time'].append(player_recorder.scores[i][0])
                    columns['score_value'].append(player_recorder.scores[i][1])
                else:
                    columns['score_time'].append(None)
                    columns['score_value'].append(None)

                if i < len(player_recorder.shots_fired):
                    columns['shot_time'].append(player_recorder.shots_fired[i])
                else:
                    columns['shot_time'].append(None)

                if i < len(player_recorder.kills):
                    columns['kill_time'].append(player_recorder.kills[i])
                else:
                    columns['kill_time'].append(None)

                if i < len(player_recorder.deaths):
                    columns['death_time'].append(player_recorder.deaths[i])
                else:
                    columns['death_time'].append(None)


        return pd.DataFrame(columns)

def create_results_viewer(menu_input, screen):
    """A factory function for ResultsViewer.

    Arguments:
        `menu_input`: A MenuInput
            The inputs of the ResultsViewer
        `screen`: A Screen
            The Screen to which the ResultsViewer will be rendered to
    """
    dataframe_renderer = DataFrameRenderer(
        cell_size=(0.22, 0.05),
        font_color=(50, 69, 63),
        max_cell_text_length=10
    )

    plotter = Plotter()
    results_renderer = ResultsRenderer(screen, dataframe_renderer, plotter)

    return ResultsViewer(menu_input, results_renderer,
                         Clock(2, sleep_wait, False))

class StatsViewer:
    """The base class for views showing statistics."""
    def __init__(self, menu_input, clock):
        """Initializes a StatsViewer.

        Arguments:
            `menu_input`: A MenuInput class
            `clock`: A Clock class
                The Clock used to set the refreshing rate for the viewer.
        """
        self._menu_input = menu_input
        self._clock = clock
        self._should_quit = False

    def _run(self, render_function):
        """A wrapper class for a `render_function`.

        Handles quit inputs and calls `render_function` according to
        self._clock.

        Should be called from the derived classes.
        """

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
        """Initializes a ResultsViewer.

        Arguments:
            `menu_input`: A MenuInput
                The inputs of the ResultsViewer
            `results_renderer`: A ResultsRenderer
                The class responsible for rendering the ResultsViewer
            `clock`: A Clock
                The Clock setting the refresh rate of `self.run()`
        """
        super().__init__(menu_input, clock)
        self._renderer = results_renderer

    def run(self, round_stats):
        """Opens the ResultsViewer for `round_stats`.

        Arguments:
            `round_stats`: A RoundStats
                The round statistics to be viewed
        """
        summary_table = round_stats.get_summary_table()
        verbose_table = round_stats.get_verbose_table()
        round_length = round_stats.get_round_length()
        self._run(
            lambda : self._renderer.render(summary_table, verbose_table,
                                           round_length)
        )


class UserStats:
    """A class for storing the user's statistics collected over many rounds.

    Attributes:
        `user`: A User
            The associated User
        `score`: A float
        `shots`: An integer
            Shots fired by the User
        `kills`: An integer
        `deaths`: An integer
        `rounds`: An integer
            The number of times the User has taken part into a Game.
    """
    def __init__(self, user, score, shots, kills, deaths, rounds):
        """Initialies UserStats.

        Arguments:
            `user`: A User
                The associated User
            `score`: A float
            `shots`: An integer
                Shots fired by the User
            `kills`: An integer
            `deaths`: An integer
            `rounds`: An integer
                The number of times the User has taken part into a Game.
        """
        self.user = user
        self.score = score
        self.shots = shots
        self.kills = kills
        self.deaths = deaths
        self.rounds = rounds

class TotalStats:
    """A class for storing the statistics collected over many rounds"""
    def __init__(self, user_stats_list):
        """Initializes TotalStats.

        Arguments:
            `user_stats_list`: A list of UserStats objects
                The UserStats objects which to include in `self`.
        """
        self._user_stats_list = sorted(user_stats_list, key=lambda x: -x.score)

    def get_summary_table(self):
        """Constructs a dataframe containing the key statistics.

        The dataframe will be sorted on descending total score.

        Returns:
            A pandas DataFrame with columns:
                'name', 'total score', 'round', 'kills', 'deaths',
                'k/d'"""
        columns = {'name': [], 'total score': [],
                   'rounds': [], 'kills': [], 'deaths': []}
        for user_stats in self._user_stats_list:
            columns['name'].append(user_stats.user.name)
            columns['total score'].append(user_stats.score)
            columns['rounds'].append(user_stats.rounds)
            columns['kills'].append(user_stats.kills)
            columns['deaths'].append(user_stats.deaths)

        data_frame = pd.DataFrame(columns)
        data_frame['k/d'] = data_frame['kills'] / data_frame['deaths']
        return data_frame

def create_high_score_viewer(stats_dao, n_top_players, menu_input, screen):
    """A factory function for HighScoreViewer.

    Arguments:
        `stats_dao`: A StatsDao
            Used to fetch the scores.
        `n_top_players`: A non-negative integer
            The number of top players whose score will be shown.
        `menu_input`: A MenuInput
            The inputs of the HighScoreViewer
        `screen`: A Screen
            The Screen to which the viewer will be rendered

    Returns:
        A HighScoreViewer
    """

    dataframe_renderer = DataFrameRenderer(
        cell_size=(0.22, 0.05),
        font_color=(50, 69, 63),
        max_cell_text_length=10
    )

    high_score_renderer = HighScoreRenderer(screen, dataframe_renderer)

    return HighScoreViewer(
        stats_dao, n_top_players, menu_input, high_score_renderer,
        Clock(2, sleep_wait, False))

class HighScoreViewer(StatsViewer):
    """A class for viewing high scores."""
    def __init__(self, stats_dao, n_top_players, menu_input, high_score_renderer,
                 clock):
        """Initializes a HighScoreViewer.

        Arguments:
            `stats_dao`: A StatsDao
                Used to fetch the scores.
            `n_top_players`: A non-negative integer
                The number of top players whose score will be shown.
            `menu_input`: A MenuInput
                The inputs of the HighScoreViewer
            `high_score_renderer`: A HighScoreRenderer
            `clock`: A Clock
                The Clock setting the refresh rate of `self.run()`
        """
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
