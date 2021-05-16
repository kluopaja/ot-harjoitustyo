from unittest.mock import Mock, ANY, create_autospec
import unittest
from pygame import Vector2
import math

from game.physics import BasePhysics, BodyPhysics, angle_between, WingPhysics, PhysicsController
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

class TestWingPhysics(unittest.TestCase):
    def setUp(self):
        tmp = BasePhysics(Vector2(0), Vector2(0), Vector2(1, 0))
        self.physics = WingPhysics(tmp, 1)
        self.only_base = BasePhysics(Vector2(0), Vector2(0), Vector2(1, 0))

    def test_wing_at_zero_angle_of_attack(self):
        self.physics.velocity = Vector2(1, 0)
        self.only_base.velocity = Vector2(1, 0)
        self.physics.update(2)
        self.only_base.update(2)
        assert (self.physics.location - self.only_base.location).magnitude() < EPS

    def test_wing_lift(self):
        self.physics.front = Vector2(1, -1)
        self.physics.front /= self.physics.front.magnitude()
        self.physics.velocity = Vector2(2, 0)
        # the pi/4 angle should cause 1 lift, so 
        # after first update velocity should be 2 * 2 * (?, -1) * 2 = (?, 8)
        self.physics.update(2)
        # and the location after second (?, -16)
        self.physics.update(2)
        assert abs(self.physics.location[1] + 16) < EPS

    def test_wing_has_drag(self):
        self.physics.front = Vector2(1, -1)
        self.physics.front /= self.physics.front.magnitude()
        self.physics.velocity = Vector2(2, 0)
        # the pi/4 angle should cause 1 drag
        # after first update velocity should be (2, ?) + 4 * (-1, ?) * 2 = (-6, 0)
        # after first update location should be (4, ?)
        self.physics.update(2)
        # after second update location should be (4, ? ) - 2 *(-6, ?) = (-8, ?)
        self.physics.update(2)
        assert abs(self.physics.location[0] + 8) < EPS

class TestPhysicsController(unittest.TestCase):
    def setUp(self):
        tmp = BasePhysics(Vector2(0), Vector2(0), Vector2(1, 0))
        self.physics = PhysicsController(tmp, 2, math.pi)

    def test_up(self):
        self.physics.up()
        self.physics.update(0.5)
        assert (self.physics.front - Vector2(0, -1)).magnitude() < EPS

    def test_down(self):
        self.physics.down()
        self.physics.update(0.5)
        assert (self.physics.front - Vector2(0, 1)).magnitude() < EPS

    def test_accelerate(self):
        self.physics.accelerate()
        self.physics.update(0.5)
        assert (self.physics.velocity - Vector2(1, 0)).magnitude() < EPS

    def test_accelerate_after_up(self):
        self.physics.up()
        self.physics.update(0.5)
        self.physics.accelerate()
        self.physics.update(0.5)
        assert (self.physics.velocity - Vector2(0, -1)).magnitude() < EPS


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
