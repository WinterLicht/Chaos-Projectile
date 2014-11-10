"""
.. module:: combatsystem
    :platform: Unix, Windows
    :synopsis: Handles collision between characters and projectiles, handles attacks etc.
"""

import events

class CombatSystem():
    """Handles collision between characters and projectiles, handles attacks etc.
    
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
        #if isinstance(event, events.CollisionOccured):
        #    self.handle_collision(event.collider_ID, event.collidee_ID)

    def update(self):
        """Update all particle emitters and remove dead objects"""
        for attack in self.world.attack.itervalues():
            attack.update()
            #Remove dead projectiles
        #check for collision
        self.check_projectile_collision()

    def check_projectile_collision(self):
        """Checks for collision between projectiles and other objects."""
        for attack_ID in self.world.attack:
            for projectile in self.world.attack[attack_ID].particles:
                for collider_ID in self.world.collider:
                    if not collider_ID == attack_ID:
                        if self.world.collider[collider_ID].colliderect(projectile.rect):
                            projectile.life = -1

#    def handle_collision(self, collider_ID, collidee_ID):
#        pass