from unittest.mock import Mock, ANY, create_autospec
import unittest
from pygame import Vector2

from game_objects import Plane, Gun
from shapes import Shape
from graphics import Graphic
from physics import PhysicsController
from game import Player

from math import pi

class TestPlane(unittest.TestCase):
    def setUp(self):
        self.shape = create_autospec(Shape)
        self.graphic = create_autospec(Graphic)
        self.plane_physics = create_autospec(PhysicsController)
        self.plane_physics.location = Vector2(1, 2)
        self.plane_physics.velocity = Vector2(1, 1)
        self.plane_physics.front = Vector2(0, 1)
        self.gun = create_autospec(Gun)
        self.gun.shoot.return_value = [Mock()]
        self.score_generator = Mock()
        self.owner = create_autospec(Player)
        self.plane = Plane(self.shape, self.graphic, self.plane_physics,
                           self.gun, self.score_generator, self.owner, health=100,
                           collision_damage = 100)
        self.plane2_physics = create_autospec(PhysicsController)
        self.plane2_physics.location = Vector2(1, 2)
        self.plane2_physics.velocity = Vector2(1, 1)
        self.plane2_physics.front = Vector2(0, 1)
        self.score_generator2 = Mock()
        self.plane2 = Plane(Mock(), Mock(), self.plane2_physics,
                            Mock(), self.score_generator2, Mock(), health = 100, collision_damage = 10)

    def test_constructor_updates_locations_to_physics_location(self):
        assert self.plane.graphic.location == Vector2(1, 2)
        assert self.plane.shape.location == Vector2(1, 2)

    def test_constructor_updates_rotations_to_physics_rotation(self):
        self.assertAlmostEqual(self.plane.graphic.rotation, -pi/2)
        self.assertAlmostEqual(self.plane.shape.rotation, -pi/2)

    def test_shoot_calls_gun_with_correct_arguments(self):
        self.plane.shoot()
        self.gun.shoot.assert_called_with(Vector2(1, 2), Vector2(1, 1),
                                          Vector2(0, 1), self.owner)

    def test_shoot_adds_bullet_to_new_objects(self):
        self.plane.shoot()
        new_objects = self.plane.new_objects()
        assert self.gun.shoot.return_value[0] in new_objects

    def test_alive_when_no_health(self):
        self.plane.health = 1
        assert self.plane.alive()

        self.plane.health = 0
        assert not self.plane.alive()

    def test_collide_damages_self_plane(self):
        self.plane.collide(self.plane2)
        assert self.plane.health == 90

    def test_collide_does_not_damage_other_plane(self):
        self.plane.collide(self.plane2)
        assert self.plane2.health == 100

    def test_collide_rewards_others_owner_correctly(self):
        self.score_generator2.return_value = 10
        self.plane2.collide(self.plane)
        self.owner.process_reward.assert_called_with(10, self.plane2.owner)

    def test_collide_does_not_reward_others_owner_if_self_is_dead(self):
        self.plane2.health = 0
        self.score_generator2.return_value = 10
        self.plane2.collide(self.plane)
        self.owner.process_reward.assert_not_called()

    def test_collide_calls_score_generator_correctly(self):
        self.plane2.collide(self.plane)
        self.score_generator2.assert_called_with(100, True)

    def test_collide_succeeds_when_other_has_no_owner(self):
        self.plane2.owner = None
        self.plane.collide(self.plane2)
        assert self.plane.health == 90

    def test_update_updates_gun_and_physics_if_alive(self):
        self.plane.update(10)
        self.gun.update.assert_called_with(10)
        self.plane_physics.update.assert_called_with(10)

    def test_update_does_not_update_gun_and_physics_if_dead(self):
        self.plane.health = 0
        self.plane.update(10)
        self.gun.update.assert_not_called()
        self.plane_physics.update.assert_not_called()

    def test_update_updates_locations(self):
        def f(x):
            self.plane_physics.location = Vector2(1, 20)
        self.plane_physics.update.side_effect = f
        self.plane.update(10)
        assert self.plane.shape.location == Vector2(1, 20)
        assert self.plane.graphic.location == Vector2(1, 20)

    def test_new_objects_contain_plane_when_alive(self):
        assert self.plane in self.plane.new_objects()

    def test_new_objects_do_not_contain_plane_when_dead(self):
        self.plane.collide(self.plane)
        assert self.plane not in self.plane.new_objects()

