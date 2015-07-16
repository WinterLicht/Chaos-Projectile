"""
.. module:: statesystem
    :platform: Unix, Windows
    :synopsis: Handles states of an entity and calls it's AI.
"""
from math import sqrt

import events
import collectible


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
        
        self.timer = 150 #timer to check if enemy should be activated

    def point_in_radius(self, radius, point1, point2):
        """Checks if a given point is in radius to the enemy.
        
        :param radius: given radius
        :type radius: int
        :param point: given point
        :type point: 2d list
        :rtype: True if point is in given radius to the enemy
        """
        vector = [point1[0] - point2[0], 
                  point1[1] - point2[1]]
        distance = sqrt(vector[0]*vector[0] + vector[1]*vector[1])
        return distance < radius

    def check_to_deactivate(self, entity_ID):
        """
        """
        if entity_ID in self.world.collider:
            radius_to_player = 900
            players_position = self.world.collider[self.world.player].center
            entity_position = self.world.collider[entity_ID].center
            if self.point_in_radius(radius_to_player, players_position, entity_position):
                if entity_ID in self.world.inactive_entities:
                    self.world.inactive_entities.remove(entity_ID)
                    if entity_ID in self.world.ai:
                        self.world.inactive_enemy_count -= 1
                        #Needed for Sound
                        ev = events.EnemyNear(entity_ID)
                        self.event_manager.post(ev)
            else:
                self.world.deactivate_entity(entity_ID)

    def notify(self, event):
        """Notify, when event occurs. 

        :param event: occured event
        :type event: events.Event
        """
        #
        if isinstance(event, events.TickEvent):
            self.timer = self.timer - 1
            if self.timer < 1:
                for entity_ID, ai in self.world.ai.iteritems():
                    self.check_to_deactivate(entity_ID)
                #Needed for sound
                if self.world.inactive_enemy_count == len(self.world.ai) - 2:
                    ev = events.NoEnemysNear()
                    self.event_manager.post(ev)
                self.timer = 150
            
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
                        if isinstance(collect, collectible.Portal):
                            ev_portal_enter = events.PortalEntered(entity_ID)
                            self.event_manager.post(ev_portal_enter)
                        else:
                            ev_collected = events.CollectedItem(entity_ID)
                            self.event_manager.post(ev_collected)
            if hasattr(event.collidee, 'tags'):
                tags = event.collidee.tags
                if tags and event.collider_ID == self.world.player:
                    if "deadly" in tags:
                        #Player dies!
                        self.world.hp[self.world.players[self.world.player].hp_ID].points = 0
                        ev_die = events.EntityDies(self.world.player)
                        self.event_manager.post(ev_die)
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
                            self.world.velocity[entity_ID].y = -vel_y
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
                if entity_ID in self.world.inactive_entities:
                    self.world.inactive_entities.remove(entity_ID)
                    if entity_ID in self.world.ai:
                        self.world.inactive_enemy_count -= 1
                        