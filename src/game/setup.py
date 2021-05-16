from utils.timing import Timer, Clock, busy_wait
from game.game import Player, GameState, Game, GameNotification
from game.game_objects import PlaneFactory
from game.inputs import GameInput, PlayerInput
from game.game_stats import UserRecorder
from graphics.game_rendering import GameRenderer, GameView, PauseOverlay, GameBackground, InfoBar
from graphics.camera import Camera
from user import UserSelector


class GameFactory:
    """A Factory class for Game.

    Attributes:
        `user_selectors`: A list of UserSelector objects
            The objects used to select the players in the next game.
            The length of the list will always be least self.get_n_players().
    """

    def __init__(self, config, user_dao, event_handler, screen, n_players=2):
        """Initializes GameFactory.

        Attributes:
            `config`: A Config class
            `user_dao`: A UserDao class
                Provides access to the user database
            `event_handler`: A EventHandler class
                The EventHandler to be used by the Game
            `screen`: A Screen
                The Screen to which the Game will be rendered
            `n_players`:
                The initial number of players selected for the Game
        """
        self._config = config
        self._level_config_selector = self._config.level_config_selector
        self._n_players = n_players
        self._user_dao = user_dao
        self._event_handler = event_handler
        self._screen = screen
        self.user_selectors = []
        self._update_players()

    def game(self):
        """Creates a Game based on the state of the `self`"""
        level_config = self._level_config_selector.get_selected()
        game_input = GameInput(self._event_handler, self._config.game_input_config)

        game_notifications = []
        plane_factories = []

        start_positions = level_config.starting_locations()

        for i in range(self._n_players):
            game_notifications.append(
                GameNotification(self._config.press_key_to_start_message,
                                 self._config.until_spawn_message))
            plane_factories.append(PlaneFactory(self._config.plane_config))
            plane_factories[i].start_position = start_positions[i]

        players = []
        game_views = []
        for i in range(self._n_players):
            player_input_config = self._config.player_input_configs[i]
            player_input = PlayerInput(game_input, player_input_config)
            user = self.user_selectors[i].get_current()
            spawn_timer = Timer(self._config.player_spawn_time)
            players.append(Player(plane_factories[i], player_input,
                                  game_notifications[i],
                                  UserRecorder(user, Timer()), user, spawn_timer))
            camera = Camera(self._config.game_camera_height)
            font_color = self._config.game_view_font_color
            game_views.append(GameView(players[-1], camera, font_color))

        game_length = self._config.game_length
        game_state = GameState(level_config.game_objects(), players,
                               level_config.name(), Timer(game_length))

        background = GameBackground.from_config(self._config.background_config)

        pause_overlay = PauseOverlay(self._config.pause_message,
                                     self._config.pause_font_color,
                                     self._config.pause_blur_radius)
        info_bar = InfoBar(self._config.info_bar_level_message,
                             self._config.info_bar_time_left_message,
                             self._config.info_bar_font_color,
                             self._config.info_bar_background_color)
        renderer = GameRenderer(self._screen, game_views, background,
                                pause_overlay, info_bar)

        game_clock = Clock(self._config.game_fps, busy_wait, True)
        game = Game(game_input, game_state, renderer, game_clock)
        return game

    def add_player(self):
        """Add a new player to the new Game"""
        self._n_players += 1
        self._update_players()

    def remove_player(self):
        """Remove a player from the new Game"""
        self._n_players -= 1
        self._update_players()

    def get_n_players(self):
        """Returns current number of players in the new Game"""
        return self._n_players

    def next_level(self):
        """Select the next level for the new Game"""
        self._level_config_selector.next_level()
        self._update_players()

    def previous_level(self):
        """Select the previous level for the new Game"""
        self._level_config_selector.previous_level()
        self._update_players()

    def get_level_name(self):
        """Returns the name of currently selected level as a string"""
        return self._level_config_selector.level_name()

    def _update_players(self):
        self._clamp_n_players()
        for i in range(len(self.user_selectors), self._n_players):
            self.user_selectors.append(UserSelector(self._user_dao))

        self.user_selectors = self.user_selectors[0:self._n_players]

    def _clamp_n_players(self):
        self._n_players = max(1, self._n_players)
        self._n_players = min(
            self._n_players, self._level_config_selector.max_players())
        self._n_players = min(
            self._n_players, len(self._config.player_input_configs))
