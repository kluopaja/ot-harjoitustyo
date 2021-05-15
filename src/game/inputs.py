import pygame

class GameInput:
    """A class for handling inputs in the Game."""
    def __init__(self, event_handler, game_input_config):
        """Initializes GameInput.

        Arguments:
            `event_handler`: A EventHandler
                Event handler used to fetch raw input events.
            `game_input_config`: A GameInputConfig
        """
        self._event_handler = event_handler
        self._config = game_input_config
        self._keymaps = {}
        self._pause_callback = lambda : None
        self.should_quit = False

    def bind_key(self, keycode, func):
        """Binds `func` to `keycode`.

        `func` will be called once if `keycode` is pressed when
        `handle_inputs` is called`.

        Arguments:
            `keycode`: A pygame key identifier code.
            `func`: A function
        """
        self._keymaps[keycode] = func

    def bind_pause(self, func):
        """Binds `func` to the pause key specified in GameInputConfig.

        The `func` will be called exactly as many times as the pause key
        was pressed.

        Arguments:
            `func`: A function
        """
        self._pause_callback = func

    def handle_inputs(self):
        """Reads all inputs and calls the bound function.

        Note:
            Quit and pause will be only triggered if corresponding keydown
            event is read from the event stream.

            Other inputs will be triggered if the corresponding key
            is pressed when its state is being queried.

            This prevents the possibility of triggering multiple quit
            or pause/unpause events if the user keeps the key pressed.
        """
        self.should_quit = False
        callbacks = self._handle_pause_and_quit()

        pressed = self._event_handler.get_pressed()

        for keycode in self._keymaps:
            if pressed[keycode]:
                callbacks.append(self._keymaps[keycode])

        for f in callbacks:
            f()

    def handle_pause_inputs(self):
        """Handles inputs during the paused game.

        Ignores input events other than pause and exit."""
        callbacks = self._handle_pause_and_quit()
        for f in callbacks:
            f()

    def _handle_pause_and_quit(self):
        callbacks = []
        for event in self._event_handler.get_events():
            if event.type == pygame.KEYDOWN:
                if event.key == self._config.quit:
                    self.should_quit = True
                elif event.key == self._config.pause:
                    callbacks.append(self._pause_callback)
        return callbacks


class PlayerInput:
    """A class for adapting a GameInput to be used to control Planes"""
    def __init__(self, game_input, player_input_config):
        """Initializes a PlayerInput.

        NOTE: Only a reference to `player_input_config` is stored!

        Arguments:
            `game_input`: A GameInput
                The object handling the inputs at lower level.
            `player_input_config`: A PlayerInputConfig
                The config file specifying the keymaps.
        """
        self._game_input = game_input
        self._config = player_input_config

    def bind_accelerate(self, func):
        """Binds the function `func` to the key meant to accelerate the Plane"""
        self._game_input.bind_key(self._config.accelerate, func)

    def bind_up(self, func):
        """Binds the function `func` to the key meant to turn the Plane up"""
        self._game_input.bind_key(self._config.up, func)

    def bind_down(self, func):
        """Binds the function `func` to the key meant to turn the Plane down"""
        self._game_input.bind_key(self._config.down, func)

    def bind_shoot(self, func):
        """Binds the function `func` to the key mean to shoot a bullet"""
        self._game_input.bind_key(self._config.shoot, func)

    def clear_shoot(self):
        """Clears the binding to the shoot key"""
        self.bind_shoot(lambda: None)

    def bind_plane(self, plane):
        """Binds all controls of Plane `plane` to `self`"""
        self.bind_accelerate(plane.accelerate)
        self.bind_up(plane.up)
        self.bind_down(plane.down)
        self.bind_shoot(plane.shoot)
