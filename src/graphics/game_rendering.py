import random
import math
from pygame import Vector2
from utils.rect_splitter import rect_splitter
class GameRenderer:
    def __init__(self, screen, game_views, game_background, pause_overlay):
        self._screen = screen
        self.game_views = game_views
        self.game_background = game_background
        self.pause_overlay = pause_overlay

        self._screen.surface.fill(self.game_background.fill_color, update=True)
        self._screen.update()

        if len(game_views) == 0:
            raise ValueError("At least 1 GameView needed")

        n_splits = math.ceil(math.log2(len(game_views)))
        whole_area = screen.surface.get_rect()
        self.game_view_areas = rect_splitter(n_splits, whole_area)

    def render(self, game_objects):
        self._render_game_objects(game_objects)
        self._screen.update()

    def render_pause(self, game_objects):
        self._render_game_objects(game_objects)
        self._screen.surface.blur(15)
        self.pause_overlay.render(self._screen.surface)
        self._screen.update()

    def _render_game_objects(self, game_objects):
        self._screen.surface.fill(self.game_background.fill_color)
        for game_view, area in zip(self.game_views, self.game_view_areas):
            subsurface = self._screen.surface.subsurface(area)
            game_view.render(subsurface, game_objects, self.game_background)

class PauseOverlay:
    def __init__(self, text, font_color):
        self.text = text
        self.font_color = font_color

    def render(self, surface):
        text_center = Vector2(surface.get_rect().center)
        surface.centered_text(self.text, text_center, self.font_color)


class GameBackground:
    def __init__(self, cloud_graphic, n_clouds, repeat_area, fill_color=(174, 186, 232)):
        """Initializes GameBackground object.

        Arguments:
            repeat_area: Vector2 object
                The size of the repeat in background.
                NOTE: Should be large enough that at most one
                copy of each cloud can be seen in each
                `render` call!
        """
        self.cloud_graphic = cloud_graphic
        self.n_clouds = n_clouds
        # TODO rename to size or something
        self.repeat_area = repeat_area
        self.fill_color = fill_color
        self.cloud_locations = self._generate_cloud_locations()

    def _generate_cloud_locations(self):
        random.seed(1337)
        result = []
        for i in range(self.n_clouds):
            result.append(Vector2(random.randint(0, self.repeat_area[0]),
                                  random.randint(0, self.repeat_area[1])))
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
        center_offset = camera.location
        for location in self.cloud_locations:
            cloud_location = self._closest_congruent(
                center_offset, location, self.repeat_area)
            self.cloud_graphic.location = cloud_location
            self.cloud_graphic.draw(camera)


def constant_view_locator(x, y):
    def _inner():
        return (x, y)
    return _inner


class GameView:
    def __init__(self, player, camera, font_color):
        self.player = player
        self.camera = camera
        self.font_color = font_color

    def render(self, surface, game_objects, game_background):
        self.camera.location = self.player.view_location()
        self.camera.set_drawing_surface(surface)

        game_background.render(self.camera)

        for game_object in game_objects:
            game_object.graphic.draw(self.camera)

        self._render_notification(surface)
        self._render_score(surface)
        self._render_name(surface)

    def _render_notification(self, surface):
        text_center = Vector2(surface.get_rect().center)
        surface.centered_text(self.player.notification.message, text_center,
                              self.font_color)

    def _render_score(self, surface):
        text_topleft = Vector2(surface.get_rect().topleft)
        surface.topleft_text(str(self.player.user_recorder.total_score()), text_topleft,
                             self.font_color)

    def _render_name(self, surface):
        text_center = Vector2(surface.get_rect().midtop)
        surface.midtop_text(str(self.player.user.name), text_center,
                            self.font_color)
