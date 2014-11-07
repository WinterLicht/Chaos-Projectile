"""
.. module:: collisionSystem
    :platform: Unix, Windows
    :synopsis: Collision system.
"""

import events

class CollisionSystem(object):
    """Moves object, checks collision, sends events for collision handling and updates image position of moved objects.
    
    Implementation is inspired by the `Pygame Platformer Examples <http://programarcadegames.com/index.php?lang=en&chapter=example_code_platformer>`_.
    
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
        #List of objects with which collision can occur
        collidee_IDs = list()
        #Filter collider, they have velocity vector and filter collidees
        #collider have a hit box.
        for entity_ID in range(len(self.world.mask)):
            if entity_ID in self.world.collider and entity_ID in self.world.velocity:
                collider_IDs.append(entity_ID)
            if entity_ID in self.world.collider:
                collidee_IDs.append(entity_ID)
        #Check collision
        for collider_ID in collider_IDs:
            old_position = self.world.collider[collider_ID].center 
            self.calculate_collision_x(collider_ID, collidee_IDs)
            self.calculate_collision_y(collider_ID, collidee_IDs)
            #Update image position of moved object
            ev = events.UpdateImagePosition(collider_ID, self.world.collider[collider_ID].center)
            self.event_manager.post(ev)
            #When moving object was a player
            if self.world.player == collider_ID:
                #Update orb direction correspondent aim direction and
                #player position
                orb_ID = self.world.charakters[collider_ID].orb_ID
                directionX = self.world.direction[orb_ID][0]
                directionY = self.world.direction[orb_ID][1]
                self.world.appearance[orb_ID].rect.center = (directionX*64 + self.world.collider[self.world.player].center[0] ,
                                                        directionY*64 + self.world.collider[self.world.player].center[1])
                if not old_position == self.world.collider[collider_ID].center:
                    #If player moved, send event 
                    ev = events.PlayerMoved(map(int, self.world.collider[collider_ID].center))
                    self.event_manager.post(ev)
                else:
                    #If not, then player stopped
                    ev = events.PlayerStoppedMovement()
                    self.event_manager.post(ev)

    def calculate_collision_x(self, collider_ID, collidee_IDs_list):
        """Move collider in x direction and check collision between collider and all other collidees.
        
        :param collider_ID: collider id
        :type collider_ID: int
        :param collidee_IDs_list: list that contains ids of all objects, with which a collision can occur
        :type collidee_IDs_list: list (int)
        """
        #Move collider in x direction.
        self.world.collider[collider_ID] = self.world.collider[collider_ID].move(self.world.velocity[collider_ID][0], 0)
        #Filter overlapping hit boxes with collider 
        hit_list = filter(lambda x:
                         self.world.collider[collider_ID].colliderect(x) and 
                         not self.world.collider[collider_ID] == x,
                         self.world.collider.itervalues())
        for element in hit_list:
            #If we are moving right, set our right side to the left side
            #of the item we hit
            if self.world.velocity[collider_ID][0] > 0:
                self.world.collider[collider_ID].right = element.left
                
            elif self.world.velocity[collider_ID][0] < 0:
            #Otherwise if we are moving left, do the opposite
                self.world.collider[collider_ID].left = element.right
        #Set new position and cast to int before, because position is in
        #pixel coordinates
        self.world.collider[collider_ID].center = map(int, self.world.collider[collider_ID].center)

    def calculate_collision_y(self, colliderID, collideeIDsList):
        """Move collider in y direction and check collision between collider and all other collidees.
        
        :param colliderID: collider id
        :type colliderID: int
        :param collideeIDsList: list that contains ids of all objects, with which a collision can occur
        :type collideeIDsList: list (int)
        """
        #Consider gravity
        self.world.state[colliderID].grounded = False
        self.world.velocity[colliderID][1] += self.gravity[1]
        #Move collider in y direction.
        self.world.collider[colliderID] = self.world.collider[colliderID].move(0, self.world.velocity[colliderID][1])
        #Filter overlapping hit boxes with collider
        #Overlapping is checked with a temp, which was moved 1 pixel
        #further than collider. This is necessary because of pixel
        #coordinates of the detected, if collider was moved 0.4 further
        temp = self.world.collider[colliderID].move(0, 1)
        hit_list = filter(lambda x:
                         temp.colliderect(x) and 
                         not self.world.collider[colliderID] == x,
                         self.world.collider.itervalues())
        for element in hit_list:
            #Reset our position based on the top/bottom of the object
            if self.world.velocity[colliderID][1] > 0:
                self.world.collider[colliderID].bottom = element.top
                if colliderID in self.world.state:
                    self.world.state[colliderID].grounded = True
            elif self.world.velocity[colliderID][1] < 0:
                self.world.collider[colliderID].top = element.bottom
            #Reset velocity in y direction, so gravity will not be added
            #every new frame
            self.world.velocity[colliderID][1] = 0
        #Set new position and cast to int before, because position is in
        #pixel coordinates
        self.world.collider[colliderID].center = map(int, self.world.collider[colliderID].center)
