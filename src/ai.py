"""
.. module:: ai
    :platform: Unix, Windows
    :synopsis: AI
"""

import random
import events


def random_(minimum, maximum=None):
    """Random integer between minimum and maximum.

    If maximum is not given, than it's assumed, that random value is between 0 and one given parameter

    :param minimum: Minimum
    :type minimum: int
    :param maximum: Maximum
    :type maximum: int
    :rtype: random integer between minimum and maximum 
    """

    if not maximum:
        maximum = minimum
        minimum = 0
    difference = maximum - minimum
    result =  int(random.random() * difference) + minimum
    return result


class AI():
    """Generic class for AI.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """
    def __init__(self, event_manager, world, entity_ID):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)

        self.world = world

        self.entity_ID = entity_ID

    def current_action(self):
        """This function is called every frame.
        
        Depending on the state of the AI this is set to an other function.
        """
        pass 


class AI_1(AI):
    """Handles simple AI.
    
    Enemy is searching for the player and attacks, if player is on the sight.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """

    def __init__(self, event_manager, world, entity_ID):
        """
        :param event_manager: event manager
        :type event_manager: events.EventManager
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        AI.__init__(self, event_manager, world, entity_ID)
        #Set idle function for the AI
        self.current_action = self.cruise

    def notify(self, event):
        """Notify, when event occurs. 

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            self.current_action()

    def cruise(self):
        """Function for simple enemy AI implements cruising logic.
        
        Enemy is walking on the level.
        """
        random_number = random_(50)
        if random_number == 1:
            self.world.state[self.entity_ID].walk_left = True
            self.world.state[self.entity_ID].walk_right = False
        if random_number == 2:
            self.world.state[self.entity_ID].walk_left = False
            self.world.state[self.entity_ID].walk_right = True
        #Check if enemy sees the player