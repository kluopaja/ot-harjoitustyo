import math
import logging
from constants import EPS
from pygame import Vector2
from graphics import ImageGraphic
from shapes import Rectangle
from physics import BasePhysics, GravityPhysics, BodyPhysics, WingPhysics, angle_between, PhysicsController

class PlaneFactory:
    def __init__(self, file_path):
        self.file_path = file_path
        self.size = Vector2(80, 40)
        self.acceleration = 4
        self.rotation = 5
        self.body_drag = 0.01
        self.wing_size = 0.3
        self.gravity = 5
        self.health = 100
        self.collision_damage = 100
        self.start_position = Vector2(0, 0)

    def plane(self, player_input):
        image_graphic = ImageGraphic.from_image_path(self.file_path,
                                                     Vector2(0, 0), self.size)
        rectangle = self._plane_rectangle(self.size)

        tmp = BasePhysics(Vector2(self.start_position), Vector2(0, 0), Vector2(1, 0))
        tmp = GravityPhysics(tmp, self.gravity)
        tmp = BodyPhysics(tmp, self.body_drag)
        tmp = WingPhysics(tmp, self.wing_size)
        plane_physics = PhysicsController(tmp, self.acceleration, self.rotation)

        plane = Plane(rectangle, image_graphic, plane_physics,
                      health=self.health, collision_damage=self.collision_damage)
        player_input.bind_to_plane(plane)
        print("new_plane")

        return plane

    def _plane_rectangle(self, size):
        return Rectangle(Vector2(-size[0]/2, -size[1]/2),
                         Vector2(size[0]/2, -size[1]/2),
                         Vector2(-size[0]/2, size[1]/2))
class Plane:
    '''
    For lift and drag see http://www.aerospaceweb.org/question/airfoils/q0150b.shtml
    '''
    def __init__(self, shape, graphic, plane_physics, health=100,
                 collision_damage=100):
        self.graphic = graphic
        self.shape = shape
        self.plane_physics = plane_physics
        self.health = health
        self.alive = True

        self.collision_damage = collision_damage

        self.location = Vector2(0)
        self.velocity = Vector2(0)
        self.front = Vector2(1.0, 0.0)

    def up(self):
        self.plane_physics.up()

    def down(self):
        self.plane_physics.down()

    def accelerate(self):
        self.plane_physics.accelerate()

    def damage(self, amount):
        self.health -= amount

    def update(self, delta_time):
        if self.health <= 0:
            self.alive = 0

        if not self.alive:
            return

        self.plane_physics.update(delta_time)

        self.location = Vector2(self.plane_physics.location)
        self.rotation = -math.radians(self.plane_physics.front.as_polar()[1])

        self.graphic.location = Vector2(self.plane_physics.location)
        self.graphic.rotation = -math.radians(self.plane_physics.front.as_polar()[1])

        self.shape.location = Vector2(self.plane_physics.location)
        self.shape.rotation = -math.radians(self.plane_physics.front.as_polar()[1])


    def new_objects(self):
        if not self.alive:
            return []

        return [self]


class Ground:
    def __init__(self, shape, graphic):
        self.graphic = graphic
        self.shape = shape
        self.collision_damage = 100

    def update(self, delta_time):
        pass

    def new_objects(self):
        return [self]

    def damage(self, amount):
        pass
