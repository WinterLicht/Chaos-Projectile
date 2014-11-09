"""
.. module:: components
    :platform: Unix, Windows
    :synopsis: All game component used.
"""

#from enum import Enum
import pygame
import chaosparticle

'''
# Enumarations: http://legacy.python.org/dev/peps/pep-0435/
class Types(Enum):
    position = 1
    appearance = 2
    collider = 3
'''
'''
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

Types = enum('position', 'appearance', 'collider', 'velocity')
'''

class Projectile(chaosparticle.Particle):
    """All projectiles are here particles even melee attacks are short living particles.
    
    :Attributes:
        - *character_ID* (int): this character fired the projectile
        - *damage* (int): damage of the projectile
    """
    
    def __init__(self, character_ID, damage, sprite_sheet, life, position, velocity,
                 acceleration):
        """
        :param character_ID: this character fired the projectile
        :type character_ID: int
        :param damage: damage of the projectile
        :type damage: int
        :param sprite_sheet: graphical representation for the particle may be one image or a sprite sheet for animated particle
        :type sprite_sheet: type may vary on Your implementation
        :param life: life time of the projectile
        :type life: int
        :param position: vector for position of a projectile
        :type position: 2d list
        :param velocity: velocity vector
        :type velocity: 2d list
        :param acceleration: acceleration vector
        :type acceleration: 2d list
        """
        chaosparticle.Particle.__init__(self, sprite_sheet, life,
                                        position, velocity,
                                        acceleration)
        self.damage = damage
        self.character_ID = character_ID


class Attack(chaosparticle.Emitter):
    """All attacks are here particle emitters.
    
    :Attributes:
        - *particles* (list): array of projectiles
        - *life*: life time of the projectiles
        - *position*: spawn position of projectiles
    """
    
    def __init__(self, character_ID, damage, position, amount,
                 sprite_sheet, life, velocity, acceleration):
        """
        :param character_ID: this character fired the projectile
        :type character_ID: int
        :param damage: damage of the projectile
        :type damage: int
        :param position: spawn position of particles
        :type position: 2d list
        :param amount: amount of spawned particles
        :type amount: positive int
        :param sprite_sheet: graphical representation for the particle may be one image or a sprite sheet for animated particle
        :type sprite_sheet: type may vary on Your implementation
        :param life: life time of all particles
        :type life: int
        :param velocity: velocity vector shows middle direction of all particles
        :type velocity: 2d list
        :param acceleration: acceleration vector
        :type acceleration: 2d list
        """
        chaosparticle.Emitter.__init__(self, position, amount, 
                                       sprite_sheet, life, velocity,
                                       acceleration)
        #Convert all the particles to projectiles
        temp = list()
        for particle in self.particles:
            projectile = Projectile(character_ID, damage,
                                    particle.sprite_sheet,
                                    particle.life, particle.position,
                                    particle.velocity,
                                    particle.acceleration)
            temp.append(projectile)
        self.particles = temp


class Collider(pygame.Rect):
    """Collider class is equal a hitbox of an entity, also stores position of entity."""
    def __init__(self, x, y, width, height):
        #pygame.Rect.__init__(self, x-width/2, y-height/2, width, height)
        pygame.Rect.__init__(self, x, y, width, height)

class Velocity(list):
    """Velocity of an entity is a simple list with two components."""
    pass

'''
class Health():
    def __init__(self, hp):
        self.hitpoints = hp
'''

class Appearance(pygame.sprite.Sprite):
    """Appearance class contains all images and animations of an entity, black is assumed to be transparent color.
    Extends pygame.sprite.Sprite.
    
    :Attributes:
        - *flip* (boolean): all images faced right, should this be flipped
        - *angle* (float): rotation angle of an image
        - *frames* (int list): for each animation of an entity stores amount of frames
        - *delay_between_frames* (int list): for each animation of an entity stores delay between frames in 1/60 seconds
        - *time* (int list): for each animation of an entity stores animation duration in 1/60 seonds
        - *current_frame_x* (int): current frame
        - *current_animation* (int): number of current animation
        - *counter* (int):counter of CPU ticks expired
        - *image_frames* (dictionary animation : number): all frames of all animations
        - *original* (pygame.Surface): stores original image of current frame without rotation or flip applied
        - *rect* (pygame.Rect): reference of current image rectangle
    """
    
    def __init__(self, sprite_sheet, width=None, height=None,
                 animations=[1], time=[0]):
        """
        :param sprite_sheet: sprite sheet
        :type sprite_sheet: pygame.Surface
        :param width: width of one single sprite or frame in pixel
        :type width: int
        :param height: height of one single sprite or frame in pixel
        :type height: int
        :param animations: contains amount of frames of each animation
        :type animations: int list
        :param time: contains duration of each animation in 1/60 seconds
        :type time: int list
        """
        pygame.sprite.Sprite.__init__(self)
        
        self.flip = False
        self.angle = 0
        #If there is no animation and the resolution is not set 
        if not width:
            width = sprite_sheet.get_width()
        if not height:
            height = sprite_sheet.get_height()

        self.frames = list()
        self.delay_between_frames = list()
        self.frames = animations
        self.time = time
        
        #Compute delay between frames for each animation
        for f in range(len(self.frames)):
            self.delay_between_frames.append(int(self.time[f] / self.frames[f]))
        
        self.current_frame_x = 0
        self.current_animation = 0
        self.counter = 0
        self.image_frames = {}
        
        #Initialize single sprites from the sprite sheet
        for animation_number in range(len(animations)):
            self.image_frames[animation_number] = list()
            for frame in range(animations[animation_number]):
                #Create a new blank image for the sprite
                image = pygame.Surface([width, height]).convert()
                #Copy the sprite from the sprite sheet
                image.blit(sprite_sheet, (0, 0), (frame*width,
                                                  animation_number*height,
                                                  width, height))
                self.image_frames[animation_number].append(image)
                #Assuming black works as the transparent color
                image.set_colorkey((0,0,0))
        #Set the image the entity starts with, here idle
        self.original = self.image_frames[0][0]
        self.image = self.image_frames[0][0]
        #Set a reference to the image rectangle
        self.rect = self.image.get_rect()

    def set_image(self, x, y=None):
        """Sets new image from the sprite sheet.
        
        :param x: frame of an animation
        :type x: int
        :param y: animation number
        :type y: int
        """
        if not y:
            y = self.current_animation
        self.original = self.image_frames[y][x]
        #Transform if necessary
        if not self.angle == 0:
            self.image = pygame.transform.rotate(self.original,
                                                 self.angle)
            self.image = pygame.transform.flip(self.image, self.flip,
                                               False)
        else:
            self.image = pygame.transform.flip(self.original, self.flip,
                                               False)

class Player():
    """Marks an entity as a player character.
    
    :Attributes:
        - *name* (string): name of the character
        - *orb_ID* (int): reference to the orb entity, that belongs this player
    """

    def __init__(self, name, orb_ID):
        """
        :param name: name of the character
        :type name: string
        :param orb_ID: reference to the orb entity, that belongs this player
        :type orb_ID: int
        """
        self.name = name
        self.orb_ID = orb_ID

class Direction(list):
    """Direction of an entity is a simple list with two components.
    
    For an character entity it is its view direction and for an orb -- its aim direction.
    """
    pass

class State():
    """Various states of an entity.
    Necessary for AI or for animation system to show appropriate animation.
    
    :Attributes:
        - *grounded* (boolean): true if entity stays on the ground
        - *walking* (boolean): true if entity is moving horizontally
        - *jumping* (boolean): true if entity is jumping or is on the air
    """

    def __init__(self):
        self.grounded = False
        self.walking = False
        self.jumping = False
        #self.aim_direction = 0
        
        #self.walk_left = False
        #self.walk_right = False
        
