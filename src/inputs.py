import pygame
class GameInput:
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.keymaps = {}
        self.should_quit = False

    def bind_keys(self, new_keymaps):
        for keycode in new_keymaps:
            if keycode in self.keymaps:
                raise Exception('Key already bound to a function')
            self.keymaps[keycode] = new_keymaps[keycode]

    def bind_key(self, keycode, func):
        self.keymaps[keycode] = func

    def handle_inputs(self):
        self.should_quit = False
        for event in self.event_handler.get_events():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.should_quit = True

        pressed = self.event_handler.get_pressed()

        callbacks = []
        for keycode in self.keymaps:
            if pressed[keycode]:
                callbacks.append(self.keymaps[keycode])

        for f in callbacks:
            f()

class PlayerInput:
    def __init__(self, game_input, up_key, left_key, right_key, shoot_key):
        self.game_input = game_input
        self.up_key = up_key
        self.left_key = left_key
        self.right_key = right_key
        self.shoot_key = shoot_key

    def bind_up(self, func):
        self.game_input.bind_key(self.up_key, func)

    def clear_up(self):
        self.bind_up(lambda : None)

    def bind_left(self, func):
        self.game_input.bind_key(self.left_key, func)

    def clear_left(self):
        self.bind_left(lambda : None)

    def bind_right(self, func):
        self.game_input.bind_key(self.right_key, func)

    def clear_right(self):
        self.bind_right(lambda : None)

    def bind_shoot(self, func):
        self.game_input.bind_key(self.shoot_key, func)

    def clear_shoot(self):
        self.bind_shoot(lambda : None)

    def bind_to_plane(self, plane):
        self.bind_up(plane.accelerate)
        self.bind_left(plane.up)
        self.bind_right(plane.down)
        self.bind_shoot(plane.shoot)
