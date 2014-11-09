"""
.. module:: combatsystem
    :platform: Unix, Windows
    :synopsis: Handles collision between characters and projectiles etc.
"""

import events

class CombatSystem():
    """Handles collision between characters and projectiles etc.
    
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
        if isinstance(event, events.TickEvent):
            self.update()
        if isinstance(event, events.CollisionOccured):
            self.handle_collision(event.collider_ID, event.collidee_ID)

    def update(self):
        for attack in self.world.attacks:
            attack.update()

    def handle_collision(self, collider_ID, collidee_ID):
        pass