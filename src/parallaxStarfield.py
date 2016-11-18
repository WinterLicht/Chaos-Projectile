"""
.. module:: parallaxStarfield
   :Platform: Unix, Windows
   :Synopsis: adapted parallax starfield from this tutorial
   http://codentronix.com/2011/04/27/a-cool-parallax-starfield-simulation-using-python/
"""

import pygame
from random import randrange, choice

MAX_STARS  = 124 # number of stars
STAR_SPEED1 = 0.3 # speed of stars in pixel
STAR_SPEED2 = 0.6
STAR_SPEED3 = 0.9

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
        - *speed* (number): speed delay for parallax effect
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
        self.speed = self.get_random_star_speed()
        self.size = choice([1,2,3])
        self.color = (255,255,255)
        self.determine_and_set_color()

    def reset(self, x_pos, y_pos):
        """ Reset star.
        
        :param x_pos: new x position in pixel
        :type x_pos: number
        :param y_pos: new y position in pixel
        :type y_pos: number
        """
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.speed = self.get_random_star_speed()
        self.size = choice([1,2,3])
        self.determine_and_set_color()

    def get_random_star_speed(self):
        """ Helper to get random speed for a star. """
        return choice([STAR_SPEED1,STAR_SPEED2,STAR_SPEED3])

    def determine_and_set_color(self):
        """ Star color depends on its parallax speed. """
        if self.speed == STAR_SPEED1:
          self.color = STAR_COLOR1
        elif self.speed == STAR_SPEED2:
          self.color = STAR_COLOR2
        elif self.speed == STAR_SPEED3:
          self.color = STAR_COLOR3

class ParallaxStarfield():
    """ Parallax starfield.

    :Attributes:
        - *screen* (pygame.Surface): game screen, where the field is drawn
        - *center_x*: x position of the camera
        - *center_y*: y position of the camera
    """
    def __init__(self, screen, center_x, center_y):
        """
        :param screen: game screen, where the field is drawn
        :type: pygame.Surface
        :param center_x: x position of the camera
        :param center_y: y position of the camera
        """
        self.screen = screen
        self.stars = []
        self.center_x = center_x
        self.center_y = center_y
        self.init_stars(screen)

    def init_stars(self, screen):
      """ Create the starfield.
      
      :param screen: on this screen starfield will be displayed
      :type screen: pygame.Surface
      """
      for i in range(MAX_STARS):
        star = Star(randrange(0, screen.get_width()-1),
                    randrange(0, screen.get_height()-1))
        self.stars.append(star)

    def move(self, center_x, center_y):
        """ Update stars.

        Considers that camera is moving in the game world and
        updates star position according camera position and
        delay/parallax speed of star.
        :param center_x: x position of the camera
        :param center_y: y position of the camera
        """
        old_center_x = self.center_x
        old_center_y = self.center_y
        diff_x = 0 # delt
        diff_y = 0
        # determine offset of moved camera (camera is centered on player)
        if (old_center_x != center_x):
            diff_x = old_center_x-center_x
            self.center_x = center_x
        if (old_center_y != center_y):
            diff_y = old_center_y-center_y
            self.center_y = center_y
        for star in self.stars:
            # d_x and d_y store the offset of moved (and centered) camera
            # plus velocity for parallax
            d_x = diff_x
            if diff_x < 0:
                d_x -= star.speed
            elif diff_x > 0:
                d_x += star.speed
            d_y = diff_y
            if diff_y < 0:
                d_y -= star.speed
            elif diff_y > 0:
                d_y += star.speed
            star.x_pos += d_x
            star.y_pos += d_y
            # If the star hit the border, reset it.
            # The one long expression is needed, when player enters teleport.
            # It resets star on area that is as large as the screen 
            if star.y_pos >= self.screen.get_height():
                star.reset(randrange(0,self.screen.get_width()-1),
                           0 if abs(diff_y < self.screen.get_height()) else randrange(0,self.screen.get_height()-1))
            elif star.y_pos < 0:
                star.reset(randrange(0, self.screen.get_width()-1),
                           self.screen.get_height()-1 if abs(diff_y < self.screen.get_height()) else randrange(0,self.screen.get_height()-1))
            if star.x_pos >= self.screen.get_width():
                star.reset(0 if abs(diff_x < self.screen.get_width()) else randrange(0,self.screen.get_width()-1),
                           randrange(0,self.screen.get_height()-1))
            elif star.x_pos < 0:
                star.reset(self.screen.get_width()-1 if abs(diff_x < self.screen.get_width()) else randrange(0,self.screen.get_width()-1),
                           randrange(0,self.screen.get_height()-1))

    def draw(self):
        """ Display starfield on screen. """
        self.screen.fill(SKY_COLOR)
        for star in self.stars:
            self.screen.fill(star.color,
                             (star.x_pos, star.y_pos, star.size, star.size))
