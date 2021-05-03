import math
from pygame import Vector2
from constants import EPS


class BasePhysics:
    def __init__(self, location, velocity, front):
        self.location = location
        self.velocity = velocity
        self.front = front
        self.acceleration = Vector2(0)

    def update(self, delta_time):
        self.velocity += delta_time * self.acceleration
        self.acceleration = Vector2(0)
        # TODO add delta_time to this!
        self.location += self.velocity


class PhysicsDecorator:
    def __init__(self, physics):
        self._physics = physics

    def update(self, delta_time):
        self._physics.update(delta_time)

    @property
    def location(self):
        return self._physics.location

    @location.setter
    def location(self, value):
        self._physics.location = value

    @property
    def velocity(self):
        return self._physics.velocity

    @velocity.setter
    def velocity(self, value):
        self._physics.velocity = value

    @property
    def front(self):
        return self._physics.front

    @front.setter
    def front(self, value):
        self._physics.front = value

    @property
    def acceleration(self):
        return self._physics.acceleration

    @acceleration.setter
    def acceleration(self, value):
        self._physics.acceleration = value


class BodyPhysics(PhysicsDecorator):
    def __init__(self, physics, body_drag, gravity):
        """Inits BodyPhysics.

        Arguments:
            `physics`: An object implementing the interface of BasePhysics.
            `body_drag`: a non-negative scalar
            `gravity`: a function Vector2 -> Vector2
                `gravity(x)` should return the gravity at `x`
        """
        super().__init__(physics)
        self.body_drag = body_drag
        self.gravity = gravity

    def update(self, delta_time):
        self.acceleration += -self.body_drag * self.velocity.magnitude() * self.velocity
        self.acceleration += self.gravity(self.location)
        self._physics.update(delta_time)


class WingPhysics(PhysicsDecorator):
    '''
    For lift and drag see http://www.aerospaceweb.org/question/airfoils/q0150b.shtml
    '''

    def __init__(self, physics, wing_size):
        super().__init__(physics)
        self.wing_size = wing_size

    def update(self, delta_time):
        self.acceleration += self._acceleration()
        self._physics.update(delta_time)

    def _acceleration(self):
        result = Vector2(0)
        angle_of_attack = self._angle_of_attack()
        result += self._calculate_wing_drag(angle_of_attack)
        result += self._calculate_wing_lift(angle_of_attack)
        return result

    def _angle_of_attack(self):
        return angle_between(self.velocity, self.front)

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

        return self.wing_size * lift_coefficient \
            * self.velocity.magnitude() * self._lift_velocity()

    def _lift_velocity(self):
        return self.velocity.rotate_rad(-math.pi/2)


class PhysicsController(PhysicsDecorator):
    def __init__(self, physics, max_acceleration, max_rotation):
        super().__init__(physics)
        self.max_acceleration = max_acceleration
        self.max_rotation = max_rotation
        self._next_rotation = 0.0
        self._next_acceleration = 0.0

    def up(self):
        self._next_rotation = self.max_rotation

    def down(self):
        self._next_rotation = -self.max_rotation

    def accelerate(self):
        self._next_acceleration = self.max_acceleration

    def update(self, delta_time):
        self.front = self._new_front(delta_time)
        self.acceleration += self._calculate_thrust()
        self._next_rotation = 0.0
        self._next_acceleration = 0.0
        self._physics.update(delta_time)

    def _new_front(self, delta_time):
        return self.front.rotate(-delta_time * math.degrees(self._next_rotation))

    def _calculate_thrust(self):
        return self._next_acceleration * self.front


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
