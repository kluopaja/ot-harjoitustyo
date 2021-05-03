from pygame import Vector2
class ResultsRenderer:
    def __init__(self, screen, dataframe_renderer, plotter,
                 user_recorder_analyzer):
        self._screen = screen
        self._dataframe_renderer = dataframe_renderer
        self._plotter = plotter
        self._analyzer = user_recorder_analyzer
        self.background_color = (186, 204, 200)
        self._aspect_ratio = 16/9

    def render(self, user_recorders):
        self._screen.surface.fill(self.background_color, update=True)
        subsurface = self._get_aspect_ratio_subsurface()

        summary_table = self._analyzer.get_sorted_summary_table(user_recorders)
        self._dataframe_renderer.render(subsurface, summary_table,
                                        (0, 0.1))

        bin_range = self._histogram_bin_range(user_recorders)

        verbose_table = self._analyzer.get_verbose_table(user_recorders)
        shot_histogram = self._plotter.plot_histogram_to_image(
            verbose_table, x="shot_time", hue='name',
            bin_range=bin_range, bins=10,
            title="Shot distribution", width=800, height=600
        )
        subsurface.draw_image_from_array(shot_histogram, (0.05, 0.3), 0.6)

        kill_histogram = self._plotter.plot_histogram_to_image(
            verbose_table, x="kill_time", hue='name',
            bin_range=bin_range, bins=10,
            title="Kill distribution", width=800, height=600
        )
        subsurface.draw_image_from_array(kill_histogram, (0.8, 0.3), 0.6)

        self._screen.update()

    def _histogram_bin_range(self, user_recorders):
        if len(user_recorders) == 0:
            return (0, 1)
        return (0, user_recorders[0].record_end_time())

    def _get_aspect_ratio_subsurface(self):
        """Creates a subsurface with suitable aspect ratio.

        Creates the maximum drawing surface fitting in `self._screen`
        that has aspect ratio `self._aspect_ratio`.
        """
        area = self._screen.surface.get_rect()
        width = area.width
        if width > self._aspect_ratio:
            area.width = self._aspect_ratio
        else:
            area.height = width / self._aspect_ratio
        area.center = Vector2(width / 2, 0.5)
        return self._screen.surface.subsurface(area)


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
