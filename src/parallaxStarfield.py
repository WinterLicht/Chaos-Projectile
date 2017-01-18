"""
.. module:: parallaxStarfield
   :Platform: Unix, Windows
   :Synopsis: adapted parallax starfield from this tutorial
   http://codentronix.com/2011/04/27/a-cool-parallax-starfield-simulation-using-python/
"""

import pygame
from random import randrange, choice

MAX_STARS1 = 80 # number of stars for each layer
MAX_STARS2 = 30
MAX_STARS3 = 14

STAR_DELAY1 = 0 # speed of stars for parallax effect
STAR_DELAY2 = 0.1 # star with small number is more far away 
STAR_DELAY3 = 0.15 # actual star speed is calculated like: camera_speed/star_delay

STAR_COLOR1 = (55,40,137) # RGD color of stars
STAR_COLOR2 = (80,70,137)
STAR_COLOR3 = (108,101,149)

SKY_COLOR = (10, 6, 28) # RGB color of background

class Star():
    """ Star class for the starfield.
    
    It is blit as a rectangle into the surface, so the position
    of the star is actually its top left corner. Stars with
    slower parallax speed are assumed more far away, so their
    color is darker.

    :Attribute:
        - *x_pos* (number): x position in game world in pixel
        - *y_pos* (number): y position in game world in pixel
        - *speed* (number): speed for parallax effect
        - *size* (number): size in pixel
        - *color* (pygame.Color): RGB color
    """

    def __init__(self, x_pos, y_pos):
        """
        :param x_pos: x position in game world in pixel
        :type x_pos: number
        :param y_pos: y position in game world in pixel
        :type y_pos: number
        """
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.speed = 0
        self.size = 1
        self.color = (255,255,255)

    def reset(self, x_pos, y_pos):
        """ Reset star position.
        
        :param x_pos: new x position in pixel
        :type x_pos: number
        :param y_pos: new y position in pixel
        :type y_pos: number
        """
        self.x_pos = x_pos
        self.y_pos = y_pos

class ParallaxStarfield():
    """ Parallax starfield.

    :Attributes:
        - *screen_w*: game screen width
        - *screen_h*: game screen height
        - *center_x*: x position of the camera
        - *center_y*: y position of the camera
    """
    def __init__(self, screen_w, screen_h, center_x, center_y):
        """
        :param screen_w: game screen width
        :param screen_h: game screen height
        :param center_x: x position of the camera
        :param center_y: y position of the camera
        """
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.stars = []
        self.center_x = center_x
        self.center_y = center_y
        self.init_stars()

    def init_stars(self):
        """ Create the starfield.
        """
        for i in range(MAX_STARS1):
            star = Star(randrange(0, self.screen_w-1),
                        randrange(0, self.screen_h-1))
            star.color = STAR_COLOR1
            star.speed = STAR_DELAY1
            star.size = 1
            self.stars.append(star)
        for i in range(MAX_STARS2):
            star = Star(randrange(0, self.screen_w-1),
                        randrange(0, self.screen_h-1))
            star.color = STAR_COLOR2
            star.speed = STAR_DELAY2
            star.size = 2
            self.stars.append(star)
        for i in range(MAX_STARS3):
            star = Star(randrange(0, self.screen_w-1),
                        randrange(0, self.screen_h-1))
            star.color = STAR_COLOR3
            star.speed = STAR_DELAY3
            star.size = 3
            self.stars.append(star)

    def move(self, center_x, center_y):
        """ Update stars.

        Considers that camera is moving in the game world and
        updates star position according camera position and
        delay/parallax speed of star.
        :param center_x: x position of the camera in world coords
        :param center_y: y position of the camera in world coords
        """
        old_center_x = self.center_x
        old_center_y = self.center_y
        diff_x = 0
        diff_y = 0
        # determine offset of moved camera
        if (old_center_x != center_x):
            diff_x = old_center_x-center_x
            self.center_x = center_x
        if (old_center_y != center_y):
            diff_y = old_center_y-center_y
            self.center_y = center_y
        for star in self.stars:
            # calculate star speed 
            d_x = diff_x * star.speed
            d_y = diff_y * star.speed
            star.x_pos += d_x
            star.y_pos += d_y
            # If the star hit the border, reset it.
            # The one long expression is needed, when player enters teleport.
            # It resets star on area that is as large as the screen 
            if star.y_pos >= self.screen_h:
                star.reset(randrange(0,self.screen_w-1),
                           0 if abs(diff_y < self.screen_h) else randrange(0,self.screen_h-1))
            elif star.y_pos < 0:
                star.reset(randrange(0, self.screen_w-1),
                           self.screen_h-1 if abs(diff_y <self.screen_h) else randrange(0,self.screen_h-1))
            if star.x_pos >= self.screen_w:
                star.reset(0 if abs(diff_x < self.screen_w) else randrange(0,self.screen_w-1),
                           randrange(0,self.screen_h-1))
            elif star.x_pos < 0:
                star.reset(self.screen_w-1 if abs(diff_x < self.screen_w) else randrange(0,self.screen_w-1),
                           randrange(0,self.screen_h-1))

    def draw(self, screen):
        """ Display starfield on screen. 
        :param screen: game screen, where starfield should be drawn
        :type screen: pygame.Surface
        """
        screen.fill(SKY_COLOR)
        for star in self.stars:
            screen.fill(star.color,
                             (star.x_pos, star.y_pos, star.size, star.size))
