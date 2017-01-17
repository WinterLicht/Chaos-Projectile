#!/usr/bin/env python
"""
.. mo5dule:: game
    :platform: Unix, Windows
    :synopsis: The main game module contains CPUSpiner to control CPU-ticks and the main game loop.
"""
# Screen strech preventing from here:
# https://bitbucket.org/pygame/pygame/src/faa5879a7e6bfe10e4e5c79d04a3d2fb65d74a62/examples/prevent_display_stretching.py?fileviewer=file-view-default

import os, sys
import pygame
import events
import gameworld
import systemmanager
import controller

class CPUSpinner:
    """Handles CPU Ticks. Every 1/60 second a Tick Event will be sent.

    :Attributes:
        - *event_manager*: event manager
        - *keep_going*: used to stop the CPUSpinner.
        - *clock*: timer
        - *fps*: frames per second
    """

    def __init__(self, event_manager):
        """
        :param event_manager: event manager
        :type event_manager: events.EventManager
        """
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.keep_going = True
        self.clock = pygame.time.Clock()
        self.fps = 60  # in milliseconds

    def run(self):
        """Run CPUSpinner and send tick events."""
        while self.keep_going:
            dt = self.clock.tick(self.fps)
            ''' ??? dt = self.clock.tick(60) / 1000. '''
            event = events.TickEvent(dt)
            self.event_manager.post(event)

    def notify(self, event):
        """Notify, when event occurs and stop CPUSpinner when it's quit event.
        
        :param event: occurred event
        :type event: events.Event
        """
        if isinstance(event, events.QuitEvent):
            #This will stop the while loop of run() method from running
            self.keep_going = False

if __name__ == "__main__":
    """Main program loop."""
    if os.name == "nt" and sys.getwindowsversion()[0] >= 6:
        print "os: Windows Vista or newer"
        # Ensure that ctypes is installed. It is included with Python 2.5 and newer,
        # but Python 2.4 users must install ctypes manually.
        try:
            import ctypes
        except ImportError:
            print('install ctypes from http://sourceforge.net/projects/ctypes/files/ctypes')
            raise
        user32 = ctypes.windll.user32
        # disable the screen stretching
        user32.SetProcessDPIAware()
    
    RESOLUTION = (800, 600)
    #Initialize PyGame and create an game window 
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Chaos Projectile')
    pygame.mouse.set_visible(True)
    #screen = pygame.display.set_mode(RESOLUTION, pygame.RESIZABLE)
    screen = pygame.display.set_mode(RESOLUTION, pygame.NOFRAME | pygame.FULLSCREEN)# | pygame.HWSURFACE)

    #Create event manager
    evManager = events.EventManager()

    #Create game world
    game = gameworld.GameWorld(screen, evManager)
    systemMngr = systemmanager.SystemManager(evManager, game)


    #Create input controller
    input_control = controller.InputController(screen, evManager)

    #CPU Tick Event
    spinner = CPUSpinner(evManager)
    spinner.run()
