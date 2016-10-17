"""
.. module:: systemmanager
   :Platform: Unix, Windows
   :Synopsis: system manager contains all game systems.
"""

import rendersystem
import collisionsystem
import inputsystem
import animationsystem
import combatsystem
import statesystem
import soundsystem


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
        self.systems.append(collisionsystem.CollisionSystem(event_manager, gameWorld))
        self.systems.append(animationsystem.AnimationSystem(event_manager, gameWorld))
        self.systems.append(inputsystem.InputSystem(event_manager, gameWorld))
        self.systems.append(statesystem.StateSystem(event_manager, gameWorld))
        self.systems.append(rendersystem.RenderSystem(event_manager, gameWorld))
        self.systems.append(combatsystem.CombatSystem(event_manager, gameWorld))
        #self.systems.append(soundsystem.SoundSystem(event_manager, gameWorld))
