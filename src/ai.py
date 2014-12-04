"""
.. module:: ai
    :platform: Unix, Windows
    :synopsis: AI
"""

import random

import events

def calculate_octant(vector):
    """Calculates in which octant vector lies and returns the normalized vector for this octant.
    
    :param vector: given vector
    :type vector: array
    :rtype: normalized vector
    """
    #Small offset between octants
    epsilon = 30
    if epsilon > vector[0] and vector[0] > -epsilon:
        direction_x = 0
    else:
        if vector[0] > 0:
            direction_x = 1
        else:
            direction_x = -1
    if epsilon > vector[1] and vector[1] > -epsilon:
        direction_y = 0
    else:
        if vector[1] > 0:
            direction_y = 1
        else:
            direction_y = -1
    #Normalize
    if not direction_y == 0 and not direction_x == 0:
        if direction_y < 0:
            direction_y = -0.75
        else:
            direction_y = 0.75
        if direction_x < 0:
            direction_x = -0.75
        else:
            direction_x = 0.75
    return (direction_x, direction_y)


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
        - *counter* (int): Helper
    """
    def __init__(self, event_manager, world, entity_ID):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.world = world
        self.entity_ID = entity_ID
        self.counter = 1

    def current_action(self, event):
        """This function is called every frame.
        
        Depending on the state of the AI this is set to an other function. May react on an event.
        
        :param event: occured event
        :type event: events.Event
        """
        pass

    def walk_left(self):
        """Walk left."""
        self.world.state[self.entity_ID].walk_left = True
        self.world.state[self.entity_ID].walk_right = False

    def walk_right(self):
        """Walk right."""
        self.world.state[self.entity_ID].walk_left = False
        self.world.state[self.entity_ID].walk_right = True

    def invert_walk_direction(self):
        """Simply inverts walk direction of the entity."""
        self.world.state[self.entity_ID].walk_left = not self.world.state[self.entity_ID].walk_left
        self.world.state[self.entity_ID].walk_right = not self.world.state[self.entity_ID].walk_right

    def random_switch_movement(self, probability):
        """Switch movement direction randomly.
        
        :param probability: Should be more than 2
        :type probability: int
        """

        random_number = random_(probability)
        if random_number == 0:
            self.walk_left()
        if random_number == 1:
            self.walk_right()

    def stop_movement(self):
        """Simply stops walking."""
        self.world.state[self.entity_ID].walk_left = False
        self.world.state[self.entity_ID].walk_right = False
        self.world.velocity[self.entity_ID][0] = 0

    def stop_attack(self):
        """Stops attacks."""
        self.world.state[self.entity_ID].attacks = -1

    def sees_player(self, player_position):
        """Checks if the player is in sight.
        
        :param player_position: players position
        :type player_position: 2d list
        :rtype: True if player seen
        """
        offset = 64
        enemys_position = self.world.collider[self.entity_ID].center
        return (player_position[1] - offset) < enemys_position[1] and \
            enemys_position[1] < (player_position[1] + offset)

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
        self.current_action = self.idle

    def notify(self, event):
        """Notify, when event occurs. 

        :param event: occured event
        :type event: events.Event
        """
        #if isinstance(event, events.TickEvent):
        self.current_action(event)

    def cruise(self, event):
        """Function for simple enemy AI implements cruising logic.

        Enemy is walking on the level.
        
        :param event: Occured event
        :typy event: events.Event
        """
        #Check if walk direction should be inverted
        if isinstance(event, events.CollisionOccured):
            self_collider = self.world.collider[self.entity_ID]
            if event.collidee.tags and event.collider_ID == self.entity_ID:
                if "corner" in event.collidee.tags:
                    if self.world.state[self.entity_ID].walk_left and \
                    self_collider.left < event.collidee.right:
                        self.invert_walk_direction()
                    elif self.world.state[self.entity_ID].walk_right and \
                    self_collider.right > event.collidee.left:
                        self.invert_walk_direction()
            random_number = random_(300)
            #Randomly go in idle state
            if random_number == 0:
                #Set duration of idle state
                self.counter = 60
                self.current_action = self.idle

        elif isinstance(event, events.TickEvent):
            #Check if enemy sees the player
            if self.sees_player(self.world.collider[self.world.player].center):
                self.current_action = self.hunt

    def idle(self, event):
        """Idle, lasts ... frames long.

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            self.stop_movement()
            self.counter -= 1
            if self.counter == 0:
                self.counter = 60
                #Start moving / cruising in an random direction
                self.random_switch_movement(2)
                self.current_action = self.cruise

    def hunt(self, event):
        """Attacks the player.

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            #Stop movement first
            self.stop_movement()
            #Get needed positions
            players_position = self.world.collider[self.world.player].center
            self_position = self.world.collider[self.entity_ID].center
            #Change aim direction
            direction = [players_position[0] - self_position[0],
                         players_position[1] - self_position[1]]
            direction = calculate_octant(direction)
            if direction[0] == 0 and direction[1] == 0:
                #Direction (0,0) is not valid
                direction = (1, 0)
            self.world.direction[self.entity_ID] = direction
            #Do attack
            self.world.state[self.entity_ID].attacks = 0
            #Check if state should be changed
            if not self.sees_player(self.world.collider[self.world.player].center):
                #Stop attacking
                self.stop_attack()
                #Set duration of idle state
                self.counter = 30
                self.current_action = self.idle

