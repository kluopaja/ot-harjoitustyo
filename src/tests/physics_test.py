from unittest.mock import Mock, ANY, create_autospec
import unittest
from pygame import Vector2
import math

from game.physics import BasePhysics, BodyPhysics, angle_between
from constants import EPS

class TestBasePhysics(unittest.TestCase):
    def setUp(self):
        self.physics = BasePhysics(Vector2(0), Vector2(0), Vector2(1, 0))

    def test_update_resets_acceleration(self):
        self.physics.acceleration = Vector2(1, 0)
        self.physics.update(0.5)
        assert self.physics.acceleration == Vector2(0)

    def test_update_updates_location_correctly(self):
        self.physics.velocity = Vector2(1, 0)
        self.physics.acceleration = Vector2(1, 0)
        self.physics.update(0.5)
        assert self.physics.location == Vector2(0.5, 0)

    def test_update_updates_velocity_correctly(self):
        self.physics.velocity = Vector2(1, 0)
        self.physics.acceleration = Vector2(1, 0)
        self.physics.update(0.5)
        assert self.physics.velocity == Vector2(1.5, 0)

class TestBodyPhysics(unittest.TestCase):
    def setUp(self):
        tmp = BasePhysics(Vector2(0), Vector2(0), Vector2(1, 0))
        self.physics = BodyPhysics(tmp, 0.5, lambda x: Vector2(0, 5))

    def test_update_only_gravity_updates_velocity_correctly(self):
        self.physics.body_drag = 0
        self.physics.update(2)
        assert self.physics.velocity == Vector2(0, 10)

    def test_update_only_body_drag_does_nothing_if_velocity_zero(self):
        self.physics.gravity = lambda x: Vector2(0)
        self.physics.update(2)
        self.physics.update(2)
        self.physics.update(2)
        self.physics.update(2)
        assert self.physics.location == Vector2(0)

    def test_equilibrium_of_gravity_and_body_drag(self):
        self.physics.velocity = Vector2(0, 1) * math.sqrt(5/self.physics.body_drag)
        self.velocity_start = Vector2(self.physics.velocity)
        self.physics.update(2)
        self.physics.update(2)
        self.physics.update(2)
        self.physics.update(2)
        self.physics.update(2)
        assert (self.physics.velocity - self.velocity_start).magnitude() < EPS

class TestAngleBetween(unittest.TestCase):
    def test_returns_zero_if_magnitude_too_small(self):
        assert angle_between(Vector2(0, EPS/2), Vector2(1)) == 0.0
        assert angle_between(Vector2(1), Vector2(0, EPS/2)) == 0.0

    def test_same_angles(self):
        assert angle_between(Vector2(1), Vector2(1)) == 0.0

    def test_small_angles(self):
        assert (angle_between(Vector2(1), Vector2(1, 0)) - (math.pi/4)) < EPS
        assert (angle_between(Vector2(1, 0), Vector2(1)) - (-math.pi/4)) < EPS

    def test_large_angles(self):
        assert (angle_between(Vector2(1, 0), Vector2(-1, -1)) - (math.pi*3/4)) < EPS
        assert (angle_between(Vector2(1, 0), Vector2(-1, 1)) - (-math.pi*3/4)) < EPS
