"""
.. module:: chaosparticle
    :platform: Unix, Windows
    :synopsis: Two dimensional particle system.
"""

# http://html5hub.com/build-a-javascript-particle-system/

import math
import numpy as np

import pygame

def get_normalized(vector):
    """Returns normalized vector or None, if vector is (0, 0).
    
    :param vector: of this vector a normalized version will be calculated
    :type vector: 2d list
    :rtype: normalized version of the vector
    """
    
    result = None
    x = vector[0]
    y = vector[1]
    if not (x == 0 and y == 0):
        #n = np.linalg.norm(vector)
        n = math.sqrt(x*x+y*y)
        result = [x/n , y/n]
    return result

def get_rotated_vector(vector, angle):
    """Returns rotated and normalized 2d vector for a given angle.

    :param vector: of this vector a rotated version will be calculated
    :type vector: 2d list
    :param angle: vector will be rotated in this angle
    :type angle: float, grad
    :rtype: rotated version of the vector
    """
    #Convert angle
    angle = (angle * math.pi)/180
    length = np.linalg.norm(vector)
    nX, nY = get_normalized(vector)
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    #Rotation for a 2d vector
    result = [nX * cos_a - nY * sin_a , nX * sin_a + nY * cos_a]
    result = result[0]*length, result[1]*length
    return result


class Particle(pygame.sprite.Sprite):
    """One Particle.
    
    :Attributes:
        - *sprite_sheet* (pygame.Surface): graphical representation for the particle may be one image or a sprite sheet for animated particle
        - *life* (int):
        - *position* (list): 2d vector for position of a particle
        - *velocity* (list): velocity vector
        - *acceleration* (list): acceleration vector can be used as gravity as well
    """
    def __init__(self, sprite_sheet, life, position, velocity, acceleration):
        """
        :param sprite_sheet: graphical representation for the particle may be one image or a sprite sheet for animated particle
        :type sprite_sheet: pygame.Surface
        :param life: life time of the particle in frames
        :type life: int
        :param position: vector for position of a particle
        :type position: 2d list
        :param velocity: velocity vector
        :type velocity: 2d list
        :param acceleration: acceleration vector
        :type acceleration: 2d list
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet
        self.rect = self.image.get_rect()
        self.life = life
        self.sprite_sheet = sprite_sheet
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration


class Emitter():
    """Particle emitter.
    
    :Attributes:
        - *particles* (list): array of particles
        - *cooldown* (int): time till new particles can be spawned in frames
        - *counter* (int): counter for the cooldown
        - *position* (2d list): spawn position of particles
        - *particle_data* (Particle): stored data for particles of this emitter
        - *amount* (int): amount of particles per one spawn
        - *spread_angle* (int): angle between velocities of the particles in grad
    """
    
    def __init__(self, cooldown, position, amount, sprite_sheet, life, velocity, acceleration, spread_angle=0):
        """
        :param cooldown: time till new particles can be spawned in frames
        :type cooldown: int
        :param position: spawn position of particles
        :type position: 2d list
        :param amount: amount of spawned particles
        :type amount: positive int
        :param sprite_sheet: graphical representation for the particle may be one image or a sprite sheet for animated particle
        :type sprite_sheet: pygame.Surface
        :param life: life time of all particles
        :type life: int
        :param velocity: velocity vector shows middle direction of all particles
        :type velocity: 2d list
        :param acceleration: acceleration vector
        :type acceleration: 2d list
        :param spread_angle: angle between velocities of the particles in grad
        :type spread_angle: int
        """
        self.cooldown = cooldown
        self.counter = 0
        self.particles = list()
        self.position = position
        self.particle_data = Particle(sprite_sheet, life, position,
                                      velocity, acceleration)
        self.amount = amount
        self.spread_angle = spread_angle

    def update(self):
        """Moves, removes dead particles and updates every attribute of particles of this emitter."""
        #Update all particles
        for particle in self.particles:
            #Move particle
            particle.velocity = np.array(particle.velocity) + \
                                np.array(particle.acceleration)
            particle.position = np.array(particle.position) + \
                                np.array(particle.velocity)
            #Update life time
            particle.life = particle.life - 1
            #Update position of the image of the particle
            particle.rect.center = particle.position
        self.remove_dead_particles()
        #Update counter so the cooldown expires
        if self.counter < (self.cooldown+1):
            self.counter = self.counter + 1

    def spawn_particles(self, velocity=None, position=None):
        """Emitter spawns particles if its cooldown expired.
        
        :param velocity: velocity of set of particles
        :type velocity: 2d list
        :param position: spawn position of particles
        :type position: 2d list
        """
        #spawn particles, if cooldown expired
        if self.counter > self.cooldown:
            if not position:
                position = self.position
            if not velocity:
                velocity = self.particle_data.velocity
            for p in range(self.amount):
                #Calculate angle of rotation of velocity vector
                angle = self.spread_angle*p#     (360 / amount) * p
                angle = angle - ((self.spread_angle*(self.amount-1)) / 2)
                #Direction of each particle is a bit rotated
                vel = get_rotated_vector(velocity, angle)
                self.particles.append(Particle(self.particle_data.sprite_sheet,
                                               self.particle_data.life,
                                               position,
                                               vel,
                                               self.particle_data.acceleration))
            #Reset counter, emitter is on the cooldown now
            self.counter = 0

    def remove_dead_particles(self):
        """Removes all particles, whose life is expired."""
        for particle in self.particles:
                if particle.life < 0:
                    self.particles.remove(particle)
