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


class Attack(chaosparticle.Emitter):
    """All attacks are here particle emitters.
    
    :Attributes:
        - *effect_ID* (int): ID of the effect of the attack
        - *particles* (list): array of projectiles
        - *position*: spawn position of projectiles
        - *damage* (int): attack damage
    """
    
    def __init__(self, damage, cooldown, position, amount,
                 sprite_sheet, life, velocity, acceleration,
                 spread_angle=0, effect_ID=None):
        """
        :param character_ID: this character fired the projectile
        :type character_ID: int
        :param damage: damage of the projectile
        :type damage: int
        :param cooldown: time till new particles can be spawned in frames
        :type cooldown: int
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
        :param spread_angle: angle between velocities of the particles in grad
        :type spread_angle: int
        """
        chaosparticle.Emitter.__init__(self, cooldown, position, amount, 
                                       sprite_sheet, life, velocity,
                                       acceleration, spread_angle)
        self.damage = damage
        self.effect_ID = effect_ID


class Collider(pygame.Rect):
    """Collider class is equal a hitbox of an entity, also stores position of entity.
    
    It stores some Tags, that can be used for special collision hndling.
    
    :Attributes:
        - *tags* (list): list of tags
    """
    def __init__(self, x, y, width, height, list_of_tags=None):
        #pygame.Rect.__init__(self, x-width/2, y-height/2, width, height)
        pygame.Rect.__init__(self, x, y, width, height)
        self.tags = list_of_tags


class Velocity(list):
    """Velocity of an entity is a simple list with two components."""
    pass


class Health():
    def __init__(self, hp, segments=None, hp_sprite_sheet=None):
        self.max = hp
        self.points = hp
        self.hp_sprites = list()
        width = 128
        height = 128
        #Store needed images
        if not segments:
            segments = 1
        if hp_sprite_sheet:
            for counter in range(segments):
                #Create a new blank image for the sprite
                image = pygame.Surface([width, height]).convert()
                #Copy the sprite from the sprite sheet
                image.blit(hp_sprite_sheet, (0, 0), (counter*width, 0,
                                                     width, height))
                self.hp_sprites.append(Appearance(image))
                #Assuming black works as the transparent color
                #image.set_colorkey((0,0,0))
            self.current_image = self.hp_sprites[segments-1]


class Appearance(pygame.sprite.Sprite):
    """Appearance class contains all images and animations of an entity, black is assumed to be transparent color.
    Extends pygame.sprite.Sprite.
    
    :Attributes:
        - *flip* (boolean): all images faced right, should this be flipped
        - *play_animation_till_end* (boolean): true if animation should be played once without interruption till it ends
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
        - *visible* (boolean): True if the animation should be shown
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

        self.play_once = False
        self.play_animation = True

        self.flip = False
        self.play_animation_till_end = False
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
            #self.image = pygame.transform.rotate(self.original,
            #                                     self.angle)
            self.image = self.rot_center(self.original, self.angle)
            self.image = pygame.transform.flip(self.image, self.flip,
                                               False)
        else:
            self.image = pygame.transform.flip(self.original, self.flip,
                                               False)
    def rot_center(self, image, angle):
        """Rotate an image while keeping its center and size."""
        '''
        orig_x = image.get_rect().center[0]
        orig_y = image.get_rect().center[1]
        rot_image = pygame.transform.rotate(image, angle)
        rot_image_rect = rot_image.get_rect()
        rot_image_rect.center = (orig_x, orig_y)
        '''
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

class Player():
    """Marks an entity as a player character.
    
    :Attributes:
        - *name* (string): name of the character
        - *orb_ID* (int): reference to the orb entity, that belongs this player
    """

    def __init__(self, orb_ID, hp_ID):
        """
        :param orb_ID: reference to the orb entity, that belongs this player
        :type orb_ID: int
        """
        self.orb_ID = orb_ID
        self.hp_ID = hp_ID

class Direction(list):
    """Direction of an entity is a simple list with two components that shows its aim/view direction."""
    pass
