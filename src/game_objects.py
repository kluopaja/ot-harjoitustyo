import math
import logging
from constants import EPS
from pygame import Vector2
from graphics import ImageGraphic
from shapes import Rectangle

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

    def plane(self, player_input):
        image_graphic = ImageGraphic.from_image_path(self.file_path,
                                                     Vector2(0, 0), self.size)
        rectangle = self._plane_rectangle(self.size)
        plane = Plane(rectangle, image_graphic, max_acceleration=self.acceleration,
                      max_rotation=self.rotation, body_drag=self.body_drag,
                      wing_size=self.wing_size, gravity=self.gravity,
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
    def __init__(self, shape, graphic, max_acceleration=4, max_rotation=5,
                 body_drag=0.01, wing_size=0.3, gravity=5, health=100,
                 collision_damage=100):
        self.graphic = graphic
        self.shape = shape
        self.max_acceleration = max_acceleration
        self.max_rotation = max_rotation
        self.body_drag = body_drag
        self.wing_size = wing_size

        self.gravity = gravity

        self.health = health
        self.alive = True

        self.collision_damage = collision_damage

        self.location = Vector2(0)
        self.velocity = Vector2(0)
        self.front = Vector2(1.0, 0.0)

        self._next_rotation = 0
        self._next_acceleration = 0

    def up(self):
        self._next_rotation = self.max_rotation

    def down(self):
        self._next_rotation = -self.max_rotation

    def accelerate(self):
        self._next_acceleration = self.max_acceleration

    def damage(self, amount):
        self.health -= amount


    def update(self, delta_time):
        if self.health <= 0:
            self.alive = 0

        if not self.alive:
            return

        new_front = self._new_front(delta_time)
        new_velocity = self._new_velocity(delta_time)
        self.front = new_front
        self.velocity = new_velocity

        self.location += self.velocity

        self._next_rotation = 0
        self._next_acceleration = 0

        self.graphic.location = Vector2(self.location)
        self.graphic.rotation = -math.radians(self.front.as_polar()[1])

        self.shape.location = Vector2(self.location)
        self.shape.rotation = -math.radians(self.front.as_polar()[1])

    def new_objects(self):
        if not self.alive:
            return []

        return [self]

    def _new_front(self, delta_time):
        return self.front.rotate(-delta_time * math.degrees(self._next_rotation))

    def _new_velocity(self, delta_time):
        d_velocity = Vector2(0, 0)
        d_velocity += self._calculate_body_drag()

        angle_of_attack = self._angle_of_attack()
        d_velocity += self._calculate_wing_drag(angle_of_attack)
        d_velocity += self._calculate_wing_lift(angle_of_attack)

        d_velocity += self._calculate_thrust()
        d_velocity += self._calculate_gravity()

        logging.debug(f"lift: {self._calculate_wing_lift(angle_of_attack)}")
        logging.debug(f"drag: {self._calculate_wing_drag(angle_of_attack)}")
        logging.debug(f"rotation: {self.front.as_polar()[1]}")
        logging.debug(f"angle_of_attack: {angle_of_attack}")

        return self.velocity + delta_time * d_velocity

    def _angle_of_attack(self):
        return angle_between(self.velocity, self.front)

    def _calculate_thrust(self):
        return self._next_acceleration * self.front

    def _calculate_body_drag(self):
        return -self.body_drag * self.velocity.magnitude() * self.velocity

    def _calculate_wing_drag(self, angle_of_attack):
        return -self.wing_size * (1 - math.cos(2*angle_of_attack)) \
               * self.velocity.magnitude() * self.velocity

    def _calculate_wing_lift(self, angle_of_attack):
        lift_coefficient = 0
        angle_mod = angle_of_attack
        if angle_mod < 0:
            angle_mod += math.pi

        if angle_mod < math.pi/9:
            lift_coefficient = angle_mod * 9 / math.pi
        elif angle_mod > math.pi - math.pi/9:
            lift_coefficient = -(math.pi - angle_mod) * 9 / math.pi
        else:
            lift_coefficient = math.sin(2*angle_mod)

        logging.debug(f'lift_coef {lift_coefficient}')
        logging.debug(f'lift_velo: {self._lift_velocity()}')

        return self.wing_size * lift_coefficient \
               * self.velocity.magnitude() * self._lift_velocity()

    def _calculate_gravity(self):
        return self.gravity * Vector2(0, 1)

    def _lift_velocity(self):
        return self.velocity.rotate_rad(-math.pi/2)

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
        logging.info("something hit ground")
        pass

def angle_between(start, end):
    '''Angle from `start` end `end`.

        Parameters:
            `start` and `end` should be pygame.Vector2

        Returns:
            `result`, the angle in radians.

            `result` is always in [-pi, pi]

        Note:
            Returns 0.0, if `start` or `end` are smaller than EPS
    '''
    if start.magnitude() < EPS or end.magnitude() < EPS:
        return 0.0

    result = math.fmod(math.radians(end.angle_to(start)), 2*math.pi)
    result = math.fmod(result + 2*math.pi, 2*math.pi)
    if result > math.pi:
        result -= 2*math.pi
    return result

