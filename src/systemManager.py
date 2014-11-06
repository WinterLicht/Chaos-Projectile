"""
.. module:: systemManager
   :Platform: Unix, Windows
   :Synopsis: system manager contains all game systems.
"""

import renderSystem
import collisionSystem
import inputSystem
import animationSystem

class SystemManager(object):
    """System manager is a container of all game systems.

    :Attributes:
        - *systems* (systems list): all systems are stored here
    """
    def __init__(self, event_manager, gameWorld):
        """
        :param event_manager: event manager
        :type event_manager: events.EventManager
        :param gameWorld: game world
        :type gameWorld: gameWorld.GameWorld
        """
        self.systems = list()
        self.systems.append(collisionSystem.CollisionSystem(event_manager, gameWorld))
        self.systems.append(animationSystem.AnimationSystem(event_manager, gameWorld))
        self.systems.append(inputSystem.InputSystem(event_manager, gameWorld))
        self.systems.append(renderSystem.RenderSystem(event_manager, gameWorld))
