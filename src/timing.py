import time
import logging
class Timer:
    def __init__(self, length):
        self.time_left = length
        self.length = length

    def start(self):
        self.time_left = self.length

    def update(self, delta_time):
        self.time_left -= delta_time

    def expired(self):
        return self.time_left <= 0

def busy_wait(until):
    while time.time() < until:
        pass

def sleep_wait(until):
    if until > time.time():
        time.sleep(until - time.time())

class Clock:
    """A class for timing the game speed.

        NOTE: Using similar class from Pygame resulted in jitter"""
    def __init__(self, fps, wait_fn):
        self.delta_time = 1/fps
        self._previous_time = time.time()
        self._last_sleep = 0
        self.wait_fn = wait_fn

    def reset(self):
        self._previous_time = time.time()
        self._last_sleep = 0

    def tick(self):
        next_time = self._previous_time + self.delta_time
        self._last_sleep = next_time - time.time()
        if self._last_sleep < 0:
            logging.warning("Skipping frames!")


        self.wait_fn(next_time)

        self._previous_time = time.time()

    def busy_fraction(self):
        return 1 - self._last_sleep / self.delta_time
