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
    """
    def __init__(self, event_manager, world, entity_ID):
        self.event_manager = event_manager
        self.event_manager.register_listener(self)

        self.world = world

        self.entity_ID = entity_ID

    def current_action(self, event):
        """This function is called every frame.
        
        Depending on the state of the AI this is set to an other function. May react on an event.
        
        :param event: occured event
        :type event: events.Event
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
            self.current_action(event)

    def cruise(self, event):
        """Function for simple enemy AI implements cruising logic.

        Enemy is walking on the level.
        
        :param event: Occured event
        :typy event: events.Event
        """
        random_number = random_(50)
        if random_number == 1:
            self.world.state[self.entity_ID].walk_left = True
            self.world.state[self.entity_ID].walk_right = False
        if random_number == 2:
            self.world.state[self.entity_ID].walk_left = False
            self.world.state[self.entity_ID].walk_right = True
        #Check if enemy sees the player
        if self.sees_player(self.world.collider[self.world.player].center):
            self.current_action = self.hunt

    def sees_player(self, player_position):
        """Checks if the player is in sight.
        
        :param player_position: players position
        :type player_position: 2d list
        :rtype: True if player seen
        """
        offset = 64
        enemys_position = self.world.collider[self.entity_ID].center
        if (player_position[1] - offset) < enemys_position[1] and enemys_position[1] < (player_position[1] + offset): 
            return True
        else:
            return False

    def hunt(self, event):
        """Attacks the player.
        
        :param event: occured event
        :type event: events.Event
        """
        players_position = self.world.collider[self.world.player].center
        self_position = self.world.collider[self.entity_ID].center
        self.world.state[self.entity_ID].attacks = 0
        #Change aim direction
        direction = [players_position[0] - self_position[0],
                     players_position[1] - self_position[1]]
        direction = calculate_octant(direction)
        if direction[0] == 0 and direction[1] == 0:
            #Direction (0,0) is not valid
            direction = (1, 0)
        self.world.direction[self.entity_ID] = direction
        #Check if state should be changed
        if not self.sees_player(self.world.collider[self.world.player].center):
            self.current_action = self.cruise
