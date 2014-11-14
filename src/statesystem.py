"""
.. module:: statesystem
    :platform: Unix, Windows
    :synopsis: Handles states of an entity and AI.
"""

import random
import events


class StateSystem():
    """Handles states of an entity and AI.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
    """

    def __init__(self, event_manager, world):
        """
        :param event_manager: event manager
        :type event_manager: events.EventManager
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        self.event_manager = event_manager
        self.event_manager.register_listener(self)

        self.world = world

    def notify(self, event):
        """Notify, when event occurs. 

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            self.update()

    def update(self):
        vel = 7
        #Handle AI
        for enemy_ID in self.world.enemies:
            self.cruise(enemy_ID)
        #Move entities
        for entity_ID in self.world.state:
            if self.world.velocity[entity_ID]:
                if self.world.state[entity_ID].walk_left:
                    self.world.velocity[entity_ID][0] = -vel
                elif not self.world.state[entity_ID].walk_right:
                    self.world.velocity[entity_ID][0] = 0
                if self.world.state[entity_ID].walk_right:
                    self.world.velocity[entity_ID][0] = vel
                elif not self.world.state[entity_ID].walk_left:
                    self.world.velocity[entity_ID][0] = 0
                if self.world.state[entity_ID].jumping and self.world.state[self.world.player].grounded:
                    self.world.velocity[self.world.player][1] = -vel*2
                    self.world.state[self.world.player].grounded = False

    def random(self, minimum, maximum=None):
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

    def cruise(self, entity_ID):
        """Function for simple enemy AI implements cruising logic.
        
        Enemy is walking on the level.
        """
        random_number = self.random(50)
        if random_number == 1:
            self.world.state[entity_ID].walk_left = True
            self.world.state[entity_ID].walk_right = False
        if random_number == 2:
            self.world.state[entity_ID].walk_left = False
            self.world.state[entity_ID].walk_right = True
