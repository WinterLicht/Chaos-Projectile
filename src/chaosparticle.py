"""
.. module:: chaosparticle
    :platform: Unix, Windows
    :synopsis: Two dimensional particle system.
"""

import math


def get_angle_between_vectors(vector_a, vector_b):
    """Get angle in arc degree between two Vectors.

    :param vector_a: first vector
    :type vector_a: 2d list
    :param vector_b: second vector
    :type vector_b: 2d list
    :rtype: angle in arc degree
    """

    #Equation:
    #A dot B = length(A)*length(B)*cos( angle_between(A, B) )
    temp = vector_a[0]*vector_b[0] + vector_a[1]*vector_b[1]
    length_a = math.sqrt(vector_a[0]*vector_a[0] + vector_a[1]*vector_a[1])
    length_b = math.sqrt(vector_b[0]*vector_b[0] + vector_b[1]*vector_b[1])
    angle = math.acos(temp/(length_a*length_b))
    #Convert angle in arc degree
    angle = (angle * 180) / math.pi
    return angle


def get_normalized(vector):
    """Returns normalized vector (2-norm) or None, if vector is (0, 0).

    :param vector: of this vector a normalized version will be calculated
    :type vector: 2d list
    :rtype: normalized version of the vector
    """

    result = None
    x = vector[0]
    y = vector[1]
    if not (x == 0 and y == 0):
        #Norm of (0,0) is not defined.
        n = math.sqrt(x*x+y*y)
        result = [x/n, y/n]
    return result


def get_rotated_vector(vector, angle):
    """Returns rotated 2d vector for a given angle counter-clockwise.

    :param vector: of this vector a rotated version will be calculated
    :type vector: 2d list
    :param angle: vector will be rotated in this angle
    :type angle: float (arc degree)
    :rtype: rotated version of the vector
    """

    #Convert angle in radiant because of math.sin/cos
    angle = (angle * math.pi)/180
    length = math.sqrt(vector[0]*vector[0] + vector[1]*vector[1])
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    #Rotation for a 2d vector
    #Equation for rotation matrix:
    #| cos( angle ) -sin( angle ) |   | x |   | rotated_x |
    #| sin( angle ) cos( angle )  | * | y | = | rotaded_y |
    result = [vector[0] * cos_a - vector[1] * sin_a,
              vector[0] * sin_a + vector[1] * cos_a]
    return result


class Particle():
    """One Particle.

    There is no rendering in this module, so type of sprite can vary.
    Particles lifetime is measured in frames, if it is negative, than
    particle will be removed. Length of velocity is speed measured in
    pixels per frame and vector direction is moving direction.

    :Attributes:
        - *sprite* ( ): graphical representation for the particle
        - *life* (int): particles lifetime
        - *position* (2d list): vector for position of a particle
        - *velocity* (2d list): velocity vector
        - *acceleration* (2d list): acceleration vector
    """

    def __init__(self, sprite, life, position, velocity, acceleration):
        """
        :param sprite: graphical representation for the particle
        :type sprite: type of your choice
        :param life: lifetime of the particle in frames
        :type life: int
        :param position: initial vector for position of a particle
        :type position: 2d list
        :param velocity: velocity vector
        :type velocity: 2d list
        :param acceleration: initial acceleration vector
        :type acceleration: 2d list
        """

        self.life = life
        self.sprite = sprite
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.angle = 0


class Emitter():
    """Particle emitter.

    Updates position of particles and takes fields into account. There
    is no rendering for particles implemented. If there are more than
    one particle spawned, than a spread angle in arc degree should be
    given. Between each of particles moving directions will be this
    angle.

    :Attributes:
        - *particles* (list): array of particles
        - *cooldown* (int): time till new particles can be spawned
        - *counter* (int): counter for the cooldown in frames
        - *position* (2d list): initial spawn position of particles
        - *particle_data* (Particle): each article has same data
        - *amount* (int): amount of particles per one spawn
        - *spread_angle* (int):
        - *fields* (list): list of gravitational fields
    """

    def __init__(self, cooldown, position, amount, sprite, life,
                 velocity, acceleration, spread_angle=0, fields=None):
        """
        :param cooldown: time till new particles can be spawned
        :type cooldown: int
        :param position: initial spawn position of particles
        :type position: 2d list
        :param amount: amount of spawned particles
        :type amount: positive int
        :param sprite: graphical representation
        :type sprite: type of your choice
        :param life: life time of all particles in frames
        :type life: int
        :param velocity: initial velocity
        :type velocity: 2d list
        :param acceleration: acceleration vector
        :type acceleration: 2d list
        :param spread_angle: angle in arc degree
        :type spread_angle: int
        :param fields: list of fields that affect particles
        :type fields: list
        """

        self.cooldown = cooldown
        self.counter = 0  # Needed for reset of the cooldown
        self.particles = list()
        self.position = position
        self.particle_data = Particle(sprite, life, position,
                                      velocity, acceleration)
        self.amount = amount
        self.spread_angle = spread_angle
        self.fields = list()
        if fields:
            self.fields = fields

    def update(self):
        """Moves, removes dead particles and updates every attribute of
        particles of this emitter.

        The rendering of particles is not implemented in this module,
        so updating the position of particles sprite should be done
        externally.

        :rtype: a list with removed particles in this update cycle
        """

        #Update all particles
        for particle in self.particles:
            self.submit_to_fields(particle)  # Fields affect particle movement
            #Move particle
            #Update velocity according to acceleration
            particle.velocity = [particle.velocity[0]+particle.acceleration[0],
                                 particle.velocity[1]+particle.acceleration[1]]
            #Update position according to velocity
            particle.position = [particle.position[0]+particle.velocity[0],
                                 particle.position[1]+particle.velocity[1]]
            particle.life = particle.life - 1
        dead_particles = self.remove_dead_particles()
        #Update counter so the cooldown expires
        if self.counter < (self.cooldown+1):
            self.counter = self.counter + 1
        return dead_particles

    def spawn_particles(self, velocity=None, position=None):
        """Emitter can spawn particles if its cooldown expired.

        :param velocity: new velocity of set of particles
        :type velocity: 2d list
        :param position: new spawn position of particles
        :type position: 2d list
        :rtype: list of particles that was spawned successfully
        """

        #Spawn particles, if cooldown expired
        new_particles = list()
        if self.counter > self.cooldown:
            if not position:
                position = self.position
            if not velocity:
                velocity = self.particle_data.velocity
            for p in range(self.amount):
                '''
                Calculate angle of rotation of moving direction for
                each particle. Assume, that first particles direction
                is equal the spread direction and the other particle
                are rotated further counter-clockwise.
                '''
                angle = self.spread_angle*p
                '''
                But the middle particle should be equal the spread
                direction, so subtract half of the angle of the whole
                spread.
                '''
                angle = angle - ((self.spread_angle*(self.amount-1)) / 2)
                vel = get_rotated_vector(velocity, angle)
                new_part = Particle(self.particle_data.sprite,
                                               self.particle_data.life,
                                               position,
                                               vel,
                                               self.particle_data.acceleration)
                new_part.angle = angle
                self.particles.append(new_part)
                new_particles.append(new_part)
            #Reset counter, emitter is on the cooldown now
            self.counter = 0
            return new_particles
        else:  # Cooldown not expired
            #No particles spawned (return empty list)
            return new_particles

    def remove_dead_particles(self):
        """Removes all particles, whose life is expired.

        :rtype: a list with removed particles in this update cycle
        """

        dead_particles = list()
        for particle in self.particles:
                if particle.life < 0:
                    dead_particles.append(particle)
                    self.particles.remove(particle)
        return dead_particles

    def submit_to_fields(self, particle):
        """Update acceleration and velocity of the particle based on
        fields.

        :param particle: particle that has to be updated
        :type particle: Particle
        """

        if self.fields:
            #Force fields affect acceleration
            total_acceleration_x = 0
            total_acceleration_y = 0
            for field in self.fields:
                #Find the distance between the particle and the field
                dist_x = field.position[0] - particle.position[0]
                dist_y = field.position[1] - particle.position[1]
                distance = math.sqrt(dist_x*dist_x+dist_y*dist_y)
                distance_pow_2 = dist_x*dist_x+dist_y*dist_y
                '''
                Newton's law of universal gravitation
                equation for gravitational field's strength:
                F = G * ((m1*m2)/r^2) where
                G is  gravitational constant
                m1 and m2 two masses
                r is the distance between the centers of the masses
                Here particles have mass 1 and the constant is adjusted
                by testing.
                '''
                force = 0.07 * ((field.mass*1.0) / distance_pow_2)
                total_acceleration_x += dist_x * force
                total_acceleration_y += dist_y * force
                particle.acceleration = [total_acceleration_x,
                                         total_acceleration_y]

    def add_field(self, field):
        """Add new field for the emitter.

        :param field: new field
        :type field: Field
        """

        self.fields.append(field)


class Field():
    """A point that attracts or repels particles.

    After "Newton's law of universal gravitation"
    (de: Gravitationsgesetz). Here positive mass attracts and negative
    repels particles.

    :Attributes:
        - *position* (2d list): position of the field
        - *mass* (int): mass of the field
    """

    def __init__(self, position, mass):
        """
        :param position: position of the field
        :type position: 2d list
        :param mass: mass
        :type mass: type
        """

        self.position = position
        self.mass = mass
