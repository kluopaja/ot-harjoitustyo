import pandas as pd
from pygame import Vector2

from plotter import Plotter
from timing import Clock, sleep_wait

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

# TODO these to a separate file
def create_results_viewer(menu_input, screen):
    dataframe_renderer = DataFrameRenderer(
        cell_size=(200, 30),
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

class ResultsRenderer:
    def __init__(self, screen, dataframe_renderer, plotter,
                 user_recorder_analyzer):
        self._screen = screen
        self._dataframe_renderer = dataframe_renderer
        self._plotter = plotter
        self._analyzer = user_recorder_analyzer
        self.background_color = (186, 204, 200)

    def render(self, user_recorders):
        self._screen.surface.fill(self.background_color)

        summary_table = self._analyzer.get_sorted_summary_table(user_recorders)
        self._dataframe_renderer.render(self._screen.surface, summary_table,
                                        (200, 200))

        bin_range = self._histogram_bin_range(user_recorders)

        verbose_table = self._analyzer.get_verbose_table(user_recorders)
        shot_histogram = self._plotter.plot_histogram_to_image(
            verbose_table, x="shot_time", hue='name',
            bin_range=bin_range, bins=10,
            title="Shot distribution", width=800, height=600
        )
        self._screen.surface.draw_image(shot_histogram, (200, 600))

        kill_histogram = self._plotter.plot_histogram_to_image(
            verbose_table, x="kill_time", hue='name',
            bin_range=bin_range, bins=10,
            title="Kill distribution", width=800, height=600
        )
        self._screen.surface.draw_image(kill_histogram, (900, 600))

        self._screen.update()

    def _histogram_bin_range(self, user_recorders):
        if len(user_recorders) == 0:
            return (0, 1)
        return (0, user_recorders[0].record_end_time())

class DataFrameRenderer:
    def __init__(self, cell_size, font_color, max_cell_text_length):
        """Initializes DataFrameRenderer

        Args:
            `cell_size`: A tuple of size 2
                The dimensions of one cell
            `font_color`: A tuple of size 3
            `max_cell_text_length`: A non-negative integer
                The maximum number of letters rendered in one cells
        """
        self.cell_size = cell_size
        self.font_color = font_color
        self.max_cell_text_length = max_cell_text_length

    def render(self, surface, df, position):
        """Renders dataframe.

        Args:
            `surface`: A DrawingSurface
             `df`: A pandas DataFrame
             `position`: a pygame Vector2
                The position of the table's top left corner
        """
        for i, text in enumerate(df.columns):
            self._render_cell(surface, text, 0, i+1, position)

        for i in range(df.shape[0]):
            self._render_cell(surface, str(i+1), i+1, 0, position)
            for j in range(df.shape[1]):
                self._render_cell(surface, str(df.iloc[i, j]), i+1, j+1, position)

    def _render_cell(self, surface, text, row, column, position):
        text = text[:self.max_cell_text_length]
        x = position[0] + column * self.cell_size[0]
        y = position[1] + row * self.cell_size[1]
        surface.topleft_text(text, (x, y), self.font_color)
