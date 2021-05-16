import random
import math
from pygame import Vector2
from utils.rect_splitter import rect_splitter
from graphics.graphics import ImageGraphic
class GameRenderer:
    """A renderer class for Game"""
    def __init__(self, screen, game_views, game_background,
                 pause_overlay, info_bar):
        """Initializes GameRenderer.

        Arguments:
            `screen`: A Screen
            `game_views`: A list of GameView objects
                The views that will be rendered to subwindows
            `game_background`: A GameBackground object
                The background rendered to each of the `game_views`
            `pause_overlay`: A PauseOverlay object
                The object rendering the pause text and effect
            `info_bar`: An InfoBar
                The object rendering the info bar

        """
        self._screen = screen
        self._game_views = game_views
        self._game_background = game_background
        self._pause_overlay = pause_overlay
        self._info_bar = info_bar

        self._screen.surface.fill(self._game_background.fill_color, update=True)
        self._screen.update()

        if len(game_views) == 0:
            raise ValueError("At least 1 GameView needed")

        n_splits = math.ceil(math.log2(len(game_views)))

        info_bar_height = self._screen.surface.get_font_height()

        self._info_bar_area = screen.surface.get_rect()
        self._info_bar_area.height = info_bar_height

        self._game_area = screen.surface.get_rect()
        self._game_area.height -= info_bar_height
        self._game_area.top += info_bar_height

        self._game_view_areas = rect_splitter(n_splits, self._game_area)

    def render(self, game_state):
        """Renders non-paused `game_state`.

        Arguments:
            `game_state`: A GameState
        """
        self._render_common(game_state)
        self._screen.update()

    def render_pause(self, game_state):
        """Renders paused `game_state`.

        Arguments:
            `game_state`: A GameState
        """
        self._render_common(game_state)
        game_area_subsurface = self._screen.surface.subsurface(self._game_area)
        self._pause_overlay.render(game_area_subsurface)
        self._screen.update()

    def _render_common(self, game_state):

        # The whole game surface needs to be cleared here
        # as the whole game surface might not be covered with
        # game views.
        # NOTE: Currently also clears the InfoBar region which is not optimal.
        self._screen.surface.fill(self._game_background.fill_color)

        for game_view, area in zip(self._game_views, self._game_view_areas):
            subsurface = self._screen.surface.subsurface(area)
            game_view.render(subsurface, game_state.game_objects,
                             self._game_background)

        info_surface = self._screen.surface.subsurface(self._info_bar_area)
        self._info_bar.render(info_surface,
                                game_state.level_name,
                                game_state.time_left())

class PauseOverlay:
    """A class for rendering the pause effect"""
    def __init__(self, text, font_color, blur_radius):
        """Initializes PauseOverlay.

        Arguments:
            `text`: A string
            `font_color`: A tuple of length 3
            `blur_radius`: A positive integer
        """
        self._text = text
        self._font_color = font_color
        self._blur_radius = blur_radius

    def render(self, surface):
        text_center = Vector2(surface.get_rect().center)
        surface.blur(self._blur_radius)
        surface.centered_text(self._text, text_center, self._font_color)

class InfoBar:
    """A class for rendering information common to all players."""
    def __init__(self, level_text, time_left_text, font_color, background_color):
        """Initializes InfoBar.

        Arguments:
            `level_text`: A string
                The text immediately in front of the level name
            `time_left_text`: A string
                The text immediately in front of the seconds left
            `font_color`: A tuple of length 3
            `background_color`: A tuple of length 3
        """
        self.level_text = level_text
        self.time_left_text = time_left_text
        self.font_color = font_color
        self.background_color = background_color

    def render(self, surface, level_name, time_left):
        """Renders InfoBar.

        Arguments:
            `surface`: A DrawingSurface
            `level_name`: A string
            `time_left`: A float
                The seconds left of the game
        """
        surface.fill(self.background_color)
        self._render_level_name(surface, level_name)
        self._render_time_left(surface, time_left)

    def _render_level_name(self, surface, level_name):
        topleft = Vector2(surface.get_rect().topleft)
        text = self.level_text + level_name
        surface.topleft_text(text, topleft, self.font_color)

    def _render_time_left(self, surface, time_left):
        midtop = Vector2(surface.get_rect().midtop)
        text = self.time_left_text + f"{max(0, time_left):4.0f}"
        surface.midtop_text(text, midtop, self.font_color)

class GameBackground:
    """A class for rendering the game background"""
    def __init__(self, graphic, n_graphics, repeat_area, fill_color):
        """Initializes GameBackground object.

        Arguments:
            `graphic`: ImageGraphic
                The graphic that is drawn to the background
            `n_graphics`: A non-negative integer
                The number of graphics in one `repeat_area`
            `repeat_area`: Vector2 object
                The size of the repeat in background.
                NOTE: Should be large enough that at most one
                copy of each cloud can be seen in each
                `render` call!
            `fill_color`: A tuple of length 3
                The color used to fill the empty space
        """
        self._graphic = graphic
        self._n_graphics = n_graphics
        # TODO rename to size or something
        self._repeat_area = repeat_area
        self.fill_color = fill_color
        self._graphic_locations = self._generate_graphic_locations()

    @classmethod
    def from_config(cls, background_config):
        """Construct a GameBackground from a config file.

        Arguments:
            `background_config` a BackgroundConfig object
        """

        background_graphic = ImageGraphic.from_image_path(
            background_config.image_file_path,
            Vector2(0, 0), Vector2(background_config.image_size))

        return cls(
            background_graphic, background_config.n_images,
            background_config.repeat_area, background_config.fill_color
        )

    def _generate_graphic_locations(self):
        random.seed(1337)
        result = []
        for i in range(self._n_graphics):
            result.append(Vector2(random.randint(0, self._repeat_area[0]),
                                  random.randint(0, self._repeat_area[1])))
        return result

    def _closest_congruent(self, target, point, mod):
        """Returns the closest point to `target`.

        Considers all points congruent with `point` modulo `mod`"""

        # Note that x % mod returns non-negative values if mod > 0
        mod_distance = Vector2((point[0] - target[0]) % mod[0],
                               (point[1] - target[1]) % mod[1])
        for i in range(2):
            if mod_distance[i]*2 > mod[i]:
                mod_distance[i] -= mod[i]

        return mod_distance + target

    def render(self, camera):
        """Renders `self` to `camera`.

        Arguments:
            `camera`: A Camera
        """
        center_offset = camera.location
        for location in self._graphic_locations:
            graphic_location = self._closest_congruent(
                center_offset, location, self._repeat_area)
            self._graphic.location = graphic_location
            self._graphic.draw(camera)

class GameView:
    """A class for rendering a single player's view to the game"""
    def __init__(self, player, camera, font_color):
        """Initializes GameView

        Arguments:
            `player`: A Player
                The player whose view is rendered
            `camera`: A Camera
                The Camera with which the view is rendered
            `font_color`: A tuple of 3
                The font color for the UI texts
        """
        self._player = player
        self._camera = camera
        self._font_color = font_color

    def render(self, surface, game_objects, game_background):
        """Renders GameView.

        Arguments:
            `surface`: A DrawingSurface
                The target to which the GameView is rendered with `self._camera`
            `game_objects`: A list of GameObject objects
                The rendered objects
            `game_background`: A GameBackground
        """

        self._camera.location = self._player.view_location()
        self._camera.set_drawing_surface(surface)

        game_background.render(self._camera)

        for game_object in game_objects:
            game_object.graphic.draw(self._camera)

        self._render_notification(surface)
        self._render_score(surface)
        self._render_name(surface)

    def _render_notification(self, surface):
        text_center = Vector2(surface.get_rect().center)
        surface.centered_text(self._player.notification.get_message(), text_center,
                              self._font_color)

    def _render_score(self, surface):
        text_topleft = Vector2(surface.get_rect().topleft)
        surface.topleft_text(str(self._player.player_recorder.total_score()),
                             text_topleft, self._font_color)

    def _render_name(self, surface):
        text_center = Vector2(surface.get_rect().midtop)
        surface.midtop_text(str(self._player.user.name), text_center,
                            self._font_color)
