"""
.. module:: level
    :platform: Unix, Windows
    :synopsis: Simple level class which loads level data from a TMX file. 
"""

import os
import pygame
import pyscroll
import pytmx.util_pygame as pytmx

class Level(object):
    """ Loads and stores level data from a TMX file.
    
    :Attributes:
        - *tmx_data* (pytmx.TiledMap): tmx data
        - *map_data* (pyscroll.data.TiledMapData): map data
    """

    def __init__(self):
        filename = self.get_map('level.tmx')
        # Load data from pyTMX
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        # Create new data source for pyScroll
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)

    def get_map(self, filename):
        """ Simple helper function to merge the file name and the directory name.
        
        :param filename: file name of TMX file
        :type filename: string
        """
        return os.path.join('data', filename)
