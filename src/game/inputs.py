import pygame


class GameInput:
    def __init__(self, event_handler, game_input_config):
        self.event_handler = event_handler
        self._config = game_input_config
        self.keymaps = {}
        self.should_quit = False
        self._pause_callback = lambda : None

    def bind_key(self, keycode, func):
        self.keymaps[keycode] = func

    def bind_pause(self, func):
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

        pressed = self.event_handler.get_pressed()

        for keycode in self.keymaps:
            if pressed[keycode]:
                callbacks.append(self.keymaps[keycode])

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
        for event in self.event_handler.get_events():
            if event.type == pygame.KEYDOWN:
                if event.key == self._config.quit:
                    self.should_quit = True
                elif event.key == self._config.pause:
                    callbacks.append(self._pause_callback)
        return callbacks


class PlayerInput:
    def __init__(self, game_input, player_input_config):
        self.game_input = game_input
        self._config = player_input_config

    def bind_up(self, func):
        self.game_input.bind_key(self._config.accelerate, func)

    def clear_up(self):
        self.bind_up(lambda: None)

    def bind_left(self, func):
        self.game_input.bind_key(self._config.up, func)

    def clear_left(self):
        self.bind_left(lambda: None)

    def bind_right(self, func):
        self.game_input.bind_key(self._config.down, func)

    def clear_right(self):
        self.bind_right(lambda: None)

    def bind_shoot(self, func):
        self.game_input.bind_key(self._config.shoot, func)

    def clear_shoot(self):
        self.bind_shoot(lambda: None)

    def bind_to_plane(self, plane):
        self.bind_up(plane.accelerate)
        self.bind_left(plane.up)
        self.bind_right(plane.down)
        self.bind_shoot(plane.shoot)
