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
        :param life: life time of the particle
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
        - *life*: life time of the particles
        - *position*: spawn position of particles
    """
    def __init__(self, position, amount, sprite_sheet, life, velocity, acceleration):
        """
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
        """
        self.particles = list()
        self.life = life
        self.position = position

        for p in range(amount):
            #30 is angle between particle velocities
            angle = 10*p#     (360 / amount) * p
            #so velocity vector is middle direction
            angle = angle - ((10*(amount-1)) / 2)
            #Direction of each particle is a bit rotated
            vel = get_rotated_vector(velocity, angle)
            self.particles.append(Particle(sprite_sheet, life, position,
                                           vel, acceleration))

    def update(self):
        """Moves and updates every attribute of particles of this emitter."""

        self.life = self.life - 1
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

'''
    def update_velocity(self):
        """Only updates velocity of the particles."""
        
        for particle in self.particles:
            particle.velocity = np.array(particle.velocity) + \
                                np.array(particle.acceleration)

    def update_position(self):
        """Only updates position of the particles, also moves them."""
        
        for particle in self.particles:
            particle.position = np.array(particle.position) + \
                                np.array(particle.velocity)

    def update_life(self):
        """Only updates life of the particle."""
        
        for particle in self.particles:
            particle.life = particle.life - 1
'''
