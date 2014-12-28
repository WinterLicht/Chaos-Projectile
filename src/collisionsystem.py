"""
.. module:: collisionsystem
    :platform: Unix, Windows
    :synopsis: Collision system.
"""

import events


class CollisionSystem(object):
    """Moves object, checks collision, sends events for collision handling and updates image position of moved objects.
    
    Characters does not collide with each other. Implementation is inspired by the `Pygame Platformer Examples <http://programarcadegames.com/index.php?lang=en&chapter=example_code_platformer>`_.
    
    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *gravity* (2D list): direction of this vector is gravity direction and length of this vector is the strength of gravity. Default is (0, 0.4)
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
                
        self.gravity = (0, 0.4)

    def notify(self, event):
        """Notify, when event occurs and check collision every tick event.
        
        :param event: occured event
        :type event: events.Event 
        """
        if isinstance(event, events.TickEvent):
            self.compute()

    def compute(self):
        """Moves object, checks collision, sends events for collision handling and updates image position of moved objects."""
        #List of moving objects
        collider_IDs = list()
        #Filter collider, they have velocity vector
        #collider have a hit box.
        for entity_ID in range(len(self.world.mask)):
            if entity_ID in self.world.velocity:#in self.world.collider and entity_ID in self.world.velocity:
                collider_IDs.append(entity_ID)
        #Check collision
        for collider_ID in collider_IDs:
            self.calculate_collision_x(collider_ID)
            self.calculate_collision_y(collider_ID)
            #Update image position of moved object
            ev = events.UpdateImagePosition(collider_ID, self.world.collider[collider_ID].center)
            self.event_manager.post(ev)
            #When moving object was a player
            if self.world.player == collider_ID:
                #Update orb direction correspondent aim direction and
                #player position
                orb_ID = self.world.players[collider_ID].orb_ID
                directionX = self.world.direction[collider_ID][0]
                directionY = self.world.direction[collider_ID][1]
                self.world.appearance[orb_ID].rect.center = (directionX*64 + self.world.collider[self.world.player].center[0] ,
                                                        directionY*64 + self.world.collider[self.world.player].center[1])
                #Update hp gui
                hp_ID = self.world.players[collider_ID].hp_ID
                self.world.appearance[hp_ID].rect.center = self.world.appearance[orb_ID].rect.center

    def calculate_collision_x(self, collider_ID):
        #Move collider in x direction.
        self.world.collider[collider_ID] = self.world.collider[collider_ID].move(self.world.velocity[collider_ID][0], 0)
        #Filter overlapping hit boxes with collider
        hit_items = self.world.tree.hit(self.world.collider[collider_ID])
        ev = None
        for element in hit_items:
            #If we are moving right, set our right side to the left side
            #of the item we hit
            if self.world.velocity[collider_ID][0] > 0:
                self.world.collider[collider_ID].right = element.left
                ev = events.EntityStopMovingRight(collider_ID)
            elif self.world.velocity[collider_ID][0] < 0:
            #Otherwise if we are moving left, do the opposite
                self.world.collider[collider_ID].left = element.right
                ev = events.EntityStopMovingLeft(collider_ID)
            #Post Event
            ev_collision = events.CollisionOccured(collider_ID, element)
            self.event_manager.post(ev_collision)
        if not hit_items:
            if self.world.velocity[collider_ID][0] > 0:
                ev = events.EntityMovesRight(collider_ID)
            elif self.world.velocity[collider_ID][0] < 0:
                ev = events.EntityMovesLeft(collider_ID)
            elif self.world.velocity[collider_ID][0] == 0:
                ev = events.EntityStopMovingLeft(collider_ID)
        if ev:
            self.event_manager.post(ev)
        #Set new position and cast to int before, because position is in
        #pixel coordinates
        self.world.collider[collider_ID].center = map(int, self.world.collider[collider_ID].center)

    def calculate_collision_y(self, collider_ID):
        #Consider gravity
        self.world.velocity[collider_ID][1] += self.gravity[1]
        #Move collider in y direction.
        self.world.collider[collider_ID] = self.world.collider[collider_ID].move(0, self.world.velocity[collider_ID][1])
        #Filter overlapping hit boxes with collider
        #Overlapping is checked with a temp, which was moved 1 pixel
        #further than collider. This is necessary because of pixel
        #coordinates of the detected, if collider was moved 0.4 further
        temp = self.world.collider[collider_ID].move(0, 1)
        hit_items = self.world.tree.hit(temp)
        ev = None
        for element in hit_items:
            #Reset our position based on the top/bottom of the object
            if self.world.velocity[collider_ID][1] > 0:
                self.world.collider[collider_ID].bottom = element.top
                ev = events.EntityGrounded(collider_ID)
            elif self.world.velocity[collider_ID][1] < 0:
                self.world.collider[collider_ID].top = element.bottom
                ev = events.EntityJump(collider_ID)
            #Reset velocity in y direction, so gravity will not be added
            #every new frame
            self.world.velocity[collider_ID][1] = 0
            #Post Event
            ev_collision = events.CollisionOccured(collider_ID, element)
            self.event_manager.post(ev_collision)
        if not hit_items:
            ev = events.EntityJump(collider_ID)
        if ev: 
            self.event_manager.post(ev)
        #Set new position and cast to int before, because position is in
        #pixel coordinates
        self.world.collider[collider_ID].center = map(int, self.world.collider[collider_ID].center)
