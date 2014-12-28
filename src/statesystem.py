"""
.. module:: statesystem
    :platform: Unix, Windows
    :synopsis: Handles states of an entity and calls it's AI.
"""

import events


class StateSystem():
    """Handles states of an entity and calls it's AI.

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
        vel = 7
        #Update first enemy AI
        for ai in self.world.ai.itervalues():
            ai.current_action(event)
            
        if isinstance(event, events.EntityMovesLeftRequest):
            self.world.velocity[event.entity_ID][0] = -vel
        if isinstance(event, events.EntityMovesRightRequest):
            self.world.velocity[event.entity_ID][0] = vel
        if isinstance(event, events.EntityStopMovingLeftRequest):
            if self.world.velocity[event.entity_ID][0] < 0:
                self.world.velocity[event.entity_ID][0] = 0
        if isinstance(event, events.EntityStopMovingRightRequest):
            if self.world.velocity[event.entity_ID][0] > 0:
                self.world.velocity[event.entity_ID][0] = 0
        if isinstance(event, events.EntityJumpRequest):
            if self.world.velocity[event.entity_ID][1] == 0:
                self.world.velocity[self.world.player][1] = -vel*2
