import pandas as pd
from pygame import Vector2

from graphics.plotter import Plotter
from utils.timing import Clock, sleep_wait
from graphics.results_rendering import DataFrameRenderer, ResultsRenderer

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

class UserRecorderAnalyzer:
    def get_sorted_summary_table(self, user_recorders):
        columns = {'name': [], 'score': [],
                   'shots_fired': [], 'kills': [], 'deaths': []}
        for user_recorder in user_recorders:
            columns['name'].append(user_recorder.user.name)
            columns['score'].append(user_recorder.total_score())
            columns['shots_fired'].append(len(user_recorder.shots_fired))
            columns['kills'].append(len(user_recorder.kills))
            columns['deaths'].append(len(user_recorder.deaths))

        df = pd.DataFrame(columns)
        df['k/d'] = df['kills'] / df['deaths']
        df['shots/kills'] = df['shots_fired'] / df['kills']
        df.sort_values(by='score', inplace=True, ascending=False, ignore_index=True)
        return df

    def get_verbose_table(self, user_recorders):
        columns = {'name': [], 'score_time': [], 'score_value': [],
                   'shot_time': [], 'kill_time': [], 'death_time': []}

        for user_recorder in user_recorders:
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
    user_recorder_analyzer = UserRecorderAnalyzer()
    results_renderer = ResultsRenderer(screen, dataframe_renderer, plotter,
                                       user_recorder_analyzer)

    return ResultsViewer(menu_input, results_renderer, Clock(2, sleep_wait))

class ResultsViewer:
    def __init__(self, menu_input, results_renderer, clock):
        self._menu_input = menu_input
        self._renderer = results_renderer
        self._clock = clock

    def run(self, user_recorders):
        self._menu_input.clear_bindings()
        self._menu_input.bind_quit(self._quit)
        self._should_quit = False
        while not self._should_quit:
            self._menu_input.handle_inputs()
            self._renderer.render(user_recorders)
            self._clock.tick()

    def _quit(self):
        self._should_quit = True

