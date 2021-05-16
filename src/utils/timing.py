import time
import logging


class Timer:
    """A resettable timer with an optional time limit.

    NOTE: Doesn't access clock but has to be updated manually."""
    def __init__(self, length=float('inf')):
        """Initializes Timer.

        Arguments:
            `length`: float
                The length of the timer
                If `inf`, then the timer can be used
                to just measure the timer from start.
        """

        self._current_time = 0
        self._length = length

    def start(self):
        """Sets the timer to 0"""
        self._current_time = 0

    def update(self, delta_time):
        """Updates the passage of time"""
        self._current_time += delta_time

    def current_time(self):
        """Returns the time passed since last time the timer was started.

        If the `self.start()` has not been called, then returns the
        time since contructor call"""
        return self._current_time

    def time_left(self):
        """Time left until expired"""
        return self._length - self._current_time

    def expired(self):
        """Returns True if the timer has expired, otherwise False"""
        return self._current_time >= self._length


def busy_wait(until):
    """A more accurate wait until `until`

    NOTE: Will use as much CPU time as possible for a single thread."""
    while time.time() < until:
        pass


def sleep_wait(until):
    """Less accurate wait until `until`.

    Uses `time.sleep` so doesn't use much CPU time"""

    if until > time.time():
        time.sleep(until - time.time())


class Clock:
    """A class for timing the game speed.

        NOTE: Using similar class from Pygame resulted in jitter.

        Attributes:
            `delta_time`: The target time between frames
        """

    def __init__(self, fps, wait_fn, log_skipping_frames):
        """Initializes Clock

        Arguments:
            `fps`: float
                The target frames per second
            `wait_fn`: either busy_wait or sleep_wait
                The function used to wait the free time between frames
            `log_skipping_frames`: boolean
                If True, then log the possible frame skips
                otherwise ignore the frame skips.

                This is to suppress the unnecessary frame skipping warnings
                in menus.
        """
        self.delta_time = 1/fps
        self._previous_time = time.time()
        self._last_sleep = 0
        self._wait_fn = wait_fn
        self._log_skipping_frames = log_skipping_frames

    def reset(self):
        """Resets timer.

        Sets the start time of the current tick.
        """
        self._previous_time = time.time()
        self._last_sleep = 0

    def tick(self):
        """Waits until end of the tick."""
        next_time = self._previous_time + self.delta_time
        self._last_sleep = next_time - time.time()
        if self._log_skipping_frames and self._last_sleep < 0:
            logging.warning("Skipping frames?")

        self._wait_fn(next_time)

        self._previous_time = time.time()

    def busy_fraction(self):
        """Returns the fraction of last frame spent outside the Clock.

        Fraction not spent waiting (either busy_wait or sleep_wait)"""
        return 1 - self._last_sleep / self.delta_time
