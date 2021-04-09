import math
import logging
from constants import EPS
from pygame import Vector2
from graphics import ImageGraphic
from shapes import Rectangle, Circle
from physics import BasePhysics, BodyPhysics, WingPhysics, angle_between, PhysicsController
from game import Timer

def score_generator(damage_score, destroying_score):
    def _inner(damage, destroyed):
        return damage * damage_score + destroyed * destroying_score
    return _inner

class PlaneFactory:
    def __init__(self, file_path, bullet_file_path):
        self.file_path = file_path
        self.bullet_file_path = bullet_file_path
        self.size = Vector2(80, 40)
        self.acceleration = 4
        self.rotation = 5
        self.body_drag = 0.01
        self.wing_size = 0.3
        self.gravity = 5
        self.health = 100
        self.collision_damage = 100
        self.start_position = Vector2(0, 0)
        self.score_generator = score_generator(0, 100)

    def plane(self, player_input, owner):
        image_graphic = ImageGraphic.from_image_path(self.file_path,
                                                     Vector2(0, 0), self.size)
        rectangle = self._plane_rectangle(self.size)

        tmp = BasePhysics(Vector2(self.start_position), Vector2(0, 0), Vector2(1, 0))
        tmp = BodyPhysics(tmp, self.body_drag, lambda x: Vector2(0, 5))
        tmp = WingPhysics(tmp, self.wing_size)
        plane_physics = PhysicsController(tmp, self.acceleration, self.rotation)

        bullet_factory = BulletFactory(self.bullet_file_path)
        gun = Gun(bullet_factory, Timer(0.2), spawn_offset=60, speed=10)

        plane = Plane(rectangle, image_graphic, plane_physics, gun, self.score_generator, owner,
                      health=self.health, collision_damage=self.collision_damage)
        player_input.bind_to_plane(plane)
        print("new_plane")

        return plane

    def _plane_rectangle(self, size):
        return Rectangle(Vector2(-size[0]/2, -size[1]/2),
                         Vector2(size[0]/2, -size[1]/2),
                         Vector2(-size[0]/2, size[1]/2))

class BulletFactory:
    def __init__(self, file_path):
        self.file_path = file_path
        self.size = Vector2(20, 20)
        self.gravity = 5
        self.body_grad = 0.001
        self.health = 1
        self.collision_damage=100

    def bullet(self, location, velocity, front, owner):
        image_graphic = ImageGraphic.from_image_path(self.file_path,
                                                     Vector2(0, 0), self.size)
        circle = Circle(Vector2(0), self.size[0]/2)
        tmp = BasePhysics(location, velocity, front)
        physics = BodyPhysics(tmp, self.body_grad, lambda x: Vector2(0, 5))
        return Bullet(circle, image_graphic, physics, owner, self.health,
                      self.collision_damage)

class Gun:
    def __init__(self, bullet_factory, timer, spawn_offset, speed):
        self.bullet_factory = bullet_factory
        self.spawn_offset = spawn_offset
        self.speed = speed
        self.timer = timer

    def update(self, delta_time):
        self.timer.update(delta_time)

    def shoot(self, location, velocity, front, owner):
        if self.timer.expired():
            self.timer.start()
            bullet_location = location + self.spawn_offset * front
            bullet_velocity = velocity + self.speed * front
            bullet_front = Vector2(front)
            return [self.bullet_factory.bullet(bullet_location, bullet_velocity, bullet_front, owner)]
        return []

class GameObject:
    def __init__(self, shape, graphic, owner, collision_damage):
        self.shape = shape
        self.graphic = graphic
        self.owner = owner
        self.collision_damage = collision_damage

    def alive(self):
        return True

    def collide(self, other):
        pass

    def update(self, delta_time):
        pass

    def new_objects(self):
        return [self]

class Plane(GameObject):
    def __init__(self, shape, graphic, plane_physics, gun, score_generator, owner, health=100,
                 collision_damage=100):
        super().__init__(shape, graphic, owner, collision_damage)

        self.plane_physics = plane_physics
        self.gun = gun
        self.score_generator = score_generator
        self.health = health

        self._new_objects = []
        self._update_locations()


    def up(self):
        self.plane_physics.up()

    def down(self):
        self.plane_physics.down()

    def accelerate(self):
        self.plane_physics.accelerate()

    def shoot(self):
        self._new_objects.extend(
            self.gun.shoot(self.plane_physics.location, self.plane_physics.velocity,
                           self.plane_physics.front, self.owner))


    def alive(self):
        return self.health > 0

    def collide(self, other):
        if not self.alive():
            return

        damage_taken, destroyed = self._damage(other.collision_damage)
        if other.owner is not None:
            other.owner.process_reward(self.score_generator(damage_taken, destroyed), self.owner)

    def _damage(self, amount):
        if not self.alive():
            return (0, False)

        damage_taken = min(amount, self.health)
        self.health -= damage_taken
        destroyed = False
        if not self.alive():
            destroyed = True

        return damage_taken, destroyed

    def update(self, delta_time):
        if not self.alive():
            return

        self.gun.update(delta_time)
        self.plane_physics.update(delta_time)

        self._update_locations()

    def _update_locations(self):
        self.graphic.location = Vector2(self.plane_physics.location)
        self.graphic.rotation = -math.radians(self.plane_physics.front.as_polar()[1])

        self.shape.location = Vector2(self.plane_physics.location)
        self.shape.rotation = -math.radians(self.plane_physics.front.as_polar()[1])

    def new_objects(self):
        if not self.alive():
            return []
        tmp = self._new_objects
        self._new_objects = []
        tmp.append(self)

        return tmp

class Bullet(GameObject):
    def __init__(self, shape, graphic, physics, owner, health=100,
                 collision_damage=100):
        super().__init__(shape, graphic, owner, collision_damage)
        self.physics = physics
        self.health = health

        self._update_locations()

    def alive(self):
        return self.health > 0

    def collide(self, other):
        if not self.alive:
            return

        damage_taken = min(other.collision_damage, self.health)
        self.health -= damage_taken

    def update(self, delta_time):
        if not self.alive():
            return

        self.physics.update(delta_time)
        self._update_locations()

    def new_objects(self):
        if not self.alive():
            return []

        return [self]

    def _update_locations(self):
        self.graphic.location = Vector2(self.physics.location)
        self.graphic.rotation = -math.radians(self.physics.front.as_polar()[1])

        self.shape.location = Vector2(self.physics.location)
        self.shape.rotation = -math.radians(self.physics.front.as_polar()[1])

class Ground(GameObject):
    def __init__(self, shape, graphic, owner=None, collision_damage=100):
        super().__init__(shape, graphic, owner, collision_damage)
