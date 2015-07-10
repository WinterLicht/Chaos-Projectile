"""
.. module:: soundsystem
   :Platform: Unix, Windows
   :Synopsis: Sound system
"""

import os
import pygame
import events
import pyscroll


class SoundSystem(object):
    """Render system.
    
    :Attributes:
        - *evManager*: event manager
        - *world*: game world
        - *screen*: game screen
    """

    def __init__(self, event_manager, world):
        """
        :param event_manager: event Manager
        :type event_manager: events.EventManager
        :param world: game world
        :type world: gameWorld.GameWorld
        """
        self.world = world
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        #Load all sounds
        filename = self.get_sound_file('Shot 3.wav')
        shot_sound = pygame.mixer.Sound(filename)
        '''
        play(5) will cause the music to played once, then repeated five times, for a total of six
        If the loops is -1 then the music will repeat indefinitely.
        '''

    def notify(self, event):
        """Notify, when event occurs and stop CPUSpinner when it's quit event. 
        
        :param event: occurred event
        :type event: events.Event
        """
        if isinstance(event, events.EntityAttacks):
            entity_ID = events.EntityAttacks
            if entity_ID == self.world.player:
                shot_sound.play()

    def get_sound_file(self, filename):
        """Simple helper function to merge the file name and the directory name.
        
        :param filename: file name of TMX file
        :type filename: string
        """
        return os.path.join('data', os.path.join('sounds', filename) )