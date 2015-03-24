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
        #Update first enemy AI
        for entity_ID, ai in self.world.ai.iteritems():
            if self.world.active_entity(entity_ID): 
                ai.current_action(event)
                
        if isinstance(event, events.CollisionOccured):
            if hasattr(event.collidee, 'entity_ID'):
                entity_ID = event.collidee.entity_ID
                if event.collidee.entity_ID in self.world.collectibles:
                    if self.world.active_entity(entity_ID):
                        collect = self.world.collectibles[entity_ID]
                        collect.handle_collision_event(event.collider_ID)
                
        if hasattr(event, 'entity_ID'):
            entity_ID = event.entity_ID
            if self.world.active_entity(entity_ID):
                if entity_ID in self.world.velocity:
                    vel_x = self.world.velocity[entity_ID].max_x
                    if isinstance(event, events.EntityMovesLeftRequest):
                        self.world.velocity[entity_ID].x = -vel_x
                    if isinstance(event, events.EntityMovesRightRequest):
                        self.world.velocity[entity_ID].x = vel_x
                    if isinstance(event, events.EntityStopMovingLeftRequest):
                        if self.world.velocity[entity_ID].x < 0:
                            self.world.velocity[entity_ID].x = 0
                    if isinstance(event, events.EntityStopMovingRightRequest):
                        if self.world.velocity[entity_ID].x > 0:
                            self.world.velocity[entity_ID].x = 0
                    vel_y = self.world.velocity[entity_ID].max_y
                    if isinstance(event, events.EntityJumpRequest):
                        if self.world.velocity[entity_ID].y == 0:
                            self.world.velocity[self.world.player].y = -vel_y
            else:
                if entity_ID in self.world.velocity:
                    #Inactive entities stop movement
                    self.world.velocity[entity_ID].x = 0
                    self.world.velocity[entity_ID].y = 0
            if isinstance(event, events.EntityDies):
                self.world.deactivate_entity(entity_ID)
            if isinstance(event, events.EntityStunned):
                self.world.deactivate_entity(entity_ID)
            if isinstance(event, events.ActivateEntity):
                self.world.inactive_entities.remove(entity_ID)
