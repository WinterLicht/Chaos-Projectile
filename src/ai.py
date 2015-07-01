"""
.. module:: ai
    :platform: Unix, Windows
    :synopsis: AI
"""

import pygame
import os

from math import sqrt
import random
import events
import chaosparticle
import components

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
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
        - *counter* (int): Helper
    """
    def __init__(self, world, entity_ID, event_manager):
        self.world = world
        self.entity_ID = entity_ID
        self.counter = 1
        self.event_manager = event_manager
        #Throws
        #RuntimeError: dictionary changed size during iteration
        #self.event_manager.register_listener(self)

    '''
    def notify(self, event):
        if self.world.active_entity(self.entity_ID):
            self.current_action(event)
    '''
    
    def current_action(self, event):
        """This function is called every frame.
        
        Depending on the state of the AI this is set to an other function. May react on an event.
        
        :param event: occured event
        :type event: events.Event
        """
        pass

    def walk_left(self):
        """Walk left."""
        ev = events.EntityMovesLeftRequest(self.entity_ID)
        self.event_manager.post(ev)

    def walk_right(self):
        """Walk right."""
        ev = events.EntityMovesRightRequest(self.entity_ID)
        self.event_manager.post(ev)

    def invert_walk_direction(self):
        """Simply inverts walk direction of the entity."""
        if self.walking_left():
            self.walk_right()
        elif self.walking_right():
            self.walk_left()

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
        ev = events.EntityStopMovingLeftRequest(self.entity_ID)
        self.event_manager.post(ev)
        ev = events.EntityStopMovingRightRequest(self.entity_ID)
        self.event_manager.post(ev)
        #self.world.velocity[self.entity_ID].x = 0

    def attack(self, attack_Nr, spawn_attack_pos=None, attack_dir=None):
        ev = events.EntityAttackRequest(self.entity_ID, attack_Nr, spawn_attack_pos, attack_dir)
        self.event_manager.post(ev)

    def walking_left(self):
        return self.world.velocity[self.entity_ID].x < 0

    def walking_right(self):
        return self.world.velocity[self.entity_ID].x > 0

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

    def point_in_radius(self, radius, point):
        """Checks if a given point is in radius to the enemy.
        
        :param radius: given radius
        :type radius: int
        :param point: given point
        :type point: 2d list
        :rtype: True if point is in given radius to the enemy
        """
        self_position = self.world.collider[self.entity_ID].center
        vector = [point[0] - self_position[0], 
                  point[1] - self_position[1]]
        distance = sqrt(vector[0]*vector[0] + vector[1]*vector[1])
        return distance < radius

class AI_1(AI):
    """Handles simple AI.
    
    Enemy is searching for the player and attacks, if player is on the sight.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """

    def __init__(self, world, entity_ID, event_manager):
        """
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        AI.__init__(self, world, entity_ID, event_manager)
        self.aggresion_range = 500
        #Set idle function for the AI
        self.current_action = self.idle

    def cruise(self, event):
        """Function for simple enemy AI implements cruising logic.

        Enemy is walking on the level.
        
        :param event: Occured event
        :typy event: events.Event
        """
        #Check if walk direction should be inverted
        if isinstance(event, events.CollisionOccured):
            self_collider = self.world.collider[self.entity_ID]
            if hasattr(event.collidee, 'tags'):
                tags = event.collidee.tags
                if tags and event.collider_ID == self.entity_ID:
                    if "corner" in tags or "deadly" in tags:
                        if self.walking_left() and self_collider.left < event.collidee.right:
                            self.invert_walk_direction()
                        elif self.walking_right() and self_collider.right > event.collidee.left:
                            self.invert_walk_direction()
            random_number = random_(300)
            #Randomly go in idle state
            if random_number == 0:
                #Set duration of idle state
                self.counter = 60
                self.current_action = self.idle

        elif isinstance(event, events.TickEvent):
            #Check if enemy sees the player and if player is in range
            players_position = self.world.collider[self.world.player].center
            if self.sees_player(players_position) and self.point_in_radius(self.aggresion_range, players_position):
                self.current_action = self.hunt

    def idle(self, event):
        """Idle, lasts ... frames long.

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            #Do not attack
            #self.stop_attack()
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
            # Flip appearance according to attack direction
            if direction[0] < 0 and not self.world.appearance[self.entity_ID].flip:
                self.world.appearance[self.entity_ID].flip = True
            elif direction[0] > 0 and self.world.appearance[self.entity_ID].flip:
                self.world.appearance[self.entity_ID].flip = False
            #Do attack
            self.attack(0, None, direction)
            #Check if state should be changed
            #Enemy doesn't sees player or player is not in range
            if not self.sees_player(self.world.collider[self.world.player].center) or not self.point_in_radius(self.aggresion_range, players_position):
                #Set duration of idle state
                self.counter = 30
                self.current_action = self.idle
                
class AI_2(AI):
    """Handles simple AI.
    
    Enemy is searching for the player and attacks, if player is on the sight.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """

    def __init__(self, world, entity_ID, event_manager):
        """
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        AI.__init__(self, world, entity_ID, event_manager)
        self.aggresion_range = 130
        #Set idle function for the AI
        self.current_action = self.idle
        self.walk_left()

    def check_near_projectiles(self, radius):
        player_att = self.world.attacks[self.world.player]
        for player_proj in player_att[0].particles:
            if (self.point_in_radius(radius, player_proj.position)):
                self.current_action = self.idle
                ev = events.EntityJumpRequest(self.entity_ID)
                self.event_manager.post(ev)

    def cruise(self, event):
        """Function for simple enemy AI implements cruising logic.

        Enemy is walking on the level.
        
        :param event: Occured event
        :typy event: events.Event
        """
        #
        if isinstance(event, events.TickEvent):
            players_position = self.world.collider[self.world.player].center
            #Check if enemy sees the player and if player is in range
            if self.sees_player(players_position):
                if self.point_in_radius(self.aggresion_range, players_position):
                    self.current_action = self.hunt
                else:
                    players_position = self.world.collider[self.world.player].center
                    self_position = self.world.collider[self.entity_ID].center
                    #Change aim direction
                    direction = players_position[0] - self_position[0]
                    if direction < 0:
                        self.walk_left()
                    elif direction > 0:
                        self.walk_right()
            if not (self.point_in_radius(200, players_position)):
                self.check_near_projectiles(200)
        elif isinstance(event, events.CollisionOccured):
            self_collider = self.world.collider[self.entity_ID]
            if hasattr(event.collidee, 'tags'):
                tags = event.collidee.tags
                if tags and event.collider_ID == self.entity_ID:
                    if "corner" in tags or "deadly" in tags:
                        if self.walking_left() and self_collider.left < event.collidee.right:
                            self.invert_walk_direction()
                        elif self.walking_right() and self_collider.right > event.collidee.left:
                            self.invert_walk_direction()
            random_number = random_(700)
            #Randomly go in idle state
            if random_number == 0:
                #Set duration of idle state####
                self.counter = 60
                self.current_action = self.idle

    def idle(self, event):
        """Idle, lasts ... frames long.

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            #Do not attack
            #self.stop_attack()
            self.stop_movement()
            self.counter -= 1
            if self.counter == 0:
                self.counter = 60
                #Start moving / cruising in an random direction
                self.random_switch_movement(2)
                self.current_action = self.cruise
            players_position = self.world.collider[self.world.player].center
            if not (self.point_in_radius(200, players_position)):
                self.check_near_projectiles(200)

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
            # Flip appearance according to attack direction
            if direction[0] < 0 and not self.world.appearance[self.entity_ID].flip:
                self.world.appearance[self.entity_ID].flip = True
            elif direction[0] > 0 and self.world.appearance[self.entity_ID].flip:
                self.world.appearance[self.entity_ID].flip = False
            #Do attack
            self.attack(0, None, direction)
            #Check if state should be changed
            #Enemy doesn't sees player or player is not in range
            if not self.sees_player(self.world.collider[self.world.player].center) or not self.point_in_radius(self.aggresion_range, players_position):
                #Set duration of idle state
                self.counter = 30
                self.current_action = self.idle

class AI_3(AI):
    """Handles simple AI.
    
    Enemy is searching for the player and attacks, if player is on the sight.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """

    def __init__(self, world, entity_ID, event_manager):
        """
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        AI.__init__(self, world, entity_ID, event_manager)
        self.aggresion_range = 300
        #Set idle function for the AI
        self.current_action = self.idle

    def idle(self, event):
        """Idle, lasts ... frames long.

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            #Do not attack
            self.stop_movement()
            #Check if enemy sees the player and if player is in range
            players_position = self.world.collider[self.world.player].center
            if self.sees_player(players_position) and self.point_in_radius(self.aggresion_range, players_position):
                self.current_action = self.hunt

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
            direction = (1, 0)
            self.world.direction[self.entity_ID] = direction
            # Flip appearance according to attack direction
            if direction[0] < 0 and not self.world.appearance[self.entity_ID].flip:
                self.world.appearance[self.entity_ID].flip = True
            elif direction[0] > 0 and self.world.appearance[self.entity_ID].flip:
                self.world.appearance[self.entity_ID].flip = False
            #Do attack
            self.attack(0, None, direction)
            #Check if state should be changed
            #Enemy doesn't sees player or player is not in range
            if not self.sees_player(self.world.collider[self.world.player].center) or not self.point_in_radius(self.aggresion_range, players_position):
                #Set duration of idle state
                self.counter = 30
                self.current_action = self.idle

class AI_Boss_2(AI):
    """Handles simple AI.
    
    Enemy is searching for the player and attacks, if player is on the sight.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """

    def __init__(self, world, entity_ID, event_manager):
        """
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        AI.__init__(self, world, entity_ID, event_manager)
        #player too far away
        self.aggresion_range = 550
        #player in melee range
        self.melee_range = 250
        #player too near
        self.too_near_range = 120
        #Set idle function for the AI
        self.current_action = self.idle
        self.walk_left()

    def check_near_projectiles(self, radius):
        player_att = self.world.attacks[self.world.player]
        for player_proj in player_att[0].particles:
            if (self.point_in_radius(radius, player_proj.position)):
                self_position = self.world.collider[self.entity_ID].center
                players_position = self.world.collider[self.world.player].center
                direction = [players_position[0] - self_position[0],
                         players_position[1] - (self_position[1]+32)]
                direction = calculate_octant(direction)
                if direction[0] == 0 and direction[1] == 0:
                    #Direction (0,0) is not valid
                    direction = (1, 0)
                self.stop_movement()
                offset = 128
                self_position = self.world.collider[self.entity_ID].center
                att_position = (self_position[0] + offset*direction[0], self_position[1] + offset*direction[1])
                self.attack(0, att_position, direction)
                player_proj.life = 0

    def cruise(self, event):
        """Function for simple enemy AI implements cruising logic.

        Enemy is walking on the level.
        
        :param event: Occured event
        :typy event: events.Event
        """
        #
        if isinstance(event, events.TickEvent):
            players_position = self.world.collider[self.world.player].center
            #Check if enemy sees the player and if player is in range
            if self.point_in_radius(self.aggresion_range, players_position):
                self_position = self.world.collider[self.entity_ID].center
                #Change aim direction
                direction = [players_position[0] - self_position[0],
                             players_position[1] - self_position[1]]
                direction = calculate_octant(direction)
                if direction[0] == 0 and direction[1] == 0:
                    #Direction (0,0) is not valid
                    direction = (1, 0)
                random_number = random_(300)
                #Randomly change cooldown... minimum is 100
                self.world.attacks[self.entity_ID][2].cooldown = 100 + random_number
                '''
                # Flip appearance according to attack direction
                if direction[0] < 0 and not self.world.appearance[self.entity_ID].flip:
                    self.world.appearance[self.entity_ID].flip = True
                elif direction[0] > 0 and self.world.appearance[self.entity_ID].flip:
                    self.world.appearance[self.entity_ID].flip = False
                '''
                offset = 340
                att_position = (self_position[0] + offset*direction[0], self_position[1] + offset*direction[1])
                direction = (-direction[0], -direction[1])
                self.attack(2, att_position, direction)
                
            if self.sees_player(players_position):
                players_position = self.world.collider[self.world.player].center
                self_position = self.world.collider[self.entity_ID].center
                #Walk towards player
                direction = players_position[0] - self_position[0]
                if direction < 0:
                    self.walk_left()
                elif direction > 0:
                    self.walk_right()
                if self.point_in_radius(self.aggresion_range-150, players_position):
                    self.current_action = self.hunt
            if not (self.point_in_radius(200, players_position)):
                # When player is far enough
                # Check if he is attacking
                self.check_near_projectiles(200)
        elif isinstance(event, events.CollisionOccured):
            self_collider = self.world.collider[self.entity_ID]
            if hasattr(event.collidee, 'tags'):
                tags = event.collidee.tags
                if tags and event.collider_ID == self.entity_ID:
                    if "corner" in tags or "deadly" in tags:
                        if self.walking_left() and self_collider.left < event.collidee.right:
                            self.invert_walk_direction()
                        elif self.walking_right() and self_collider.right > event.collidee.left:
                            self.invert_walk_direction()
            random_number = random_(700)
            #Randomly go in idle state
            if random_number == 0:
                #Set duration of idle state####
                self.counter = 60
                self.current_action = self.idle

    def idle(self, event):
        """Idle, lasts ... frames long.

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            #Do not attack
            #self.stop_attack()
            self.stop_movement()
            self.counter -= 1
            if self.counter == 0:
                self.counter = 60
                #Start moving / cruising in an random direction
                self.random_switch_movement(2)
                self.current_action = self.cruise
            players_position = self.world.collider[self.world.player].center
            if not (self.point_in_radius(200, players_position)):
                self.check_near_projectiles(200)

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
            if not (self.point_in_radius(200, players_position)):
                # When player is far enough
                # Check if he is attacking
                self.check_near_projectiles(200)
            #Change aim direction
            direction = [players_position[0] - self_position[0],
                         players_position[1] - (self_position[1]+32)]
            direction = calculate_octant(direction)
            if direction[0] == 0 and direction[1] == 0:
                #Direction (0,0) is not valid
                direction = (1, 0)
            # Range to player:
            melee_range = self.point_in_radius(self.melee_range, players_position)
            too_near = self.point_in_radius(self.too_near_range, players_position)
            if melee_range and not too_near:
                # Melee range start attacking
                self.world.direction[self.entity_ID] = direction
                # Flip appearance according to attack direction
                if direction[0] < 0 and not self.world.appearance[self.entity_ID].flip:
                    self.world.appearance[self.entity_ID].flip = True
                elif direction[0] > 0 and self.world.appearance[self.entity_ID].flip:
                    self.world.appearance[self.entity_ID].flip = False
                #Do attack
                self.attack(1, None, direction)
            else:
                if too_near:
                    #small posibillity that enemy attacks normally if player is too near
                    random_number = random_(124)
                    if random_number == 0:
                        self.world.direction[self.entity_ID] = direction
                        # Flip appearance according to attack direction
                        if direction[0] < 0 and not self.world.appearance[self.entity_ID].flip:
                            self.world.appearance[self.entity_ID].flip = True
                        elif direction[0] > 0 and self.world.appearance[self.entity_ID].flip:
                            self.world.appearance[self.entity_ID].flip = False
                        #Do attack
                        self.attack(1, None, direction)   
                random_number = random_(300)
                #Randomly change cooldown... minimum is 100
                self.world.attacks[self.entity_ID][2].cooldown = 100 + random_number
                # Flip appearance according to attack direction
                if direction[0] < 0 and not self.world.appearance[self.entity_ID].flip:
                    self.world.appearance[self.entity_ID].flip = True
                elif direction[0] > 0 and self.world.appearance[self.entity_ID].flip:
                    self.world.appearance[self.entity_ID].flip = False
                #
                offset = 340
                att_position = (self_position[0] + offset*direction[0], self_position[1] + offset*direction[1])
                direction = (-direction[0], -direction[1])
                self.attack(2, att_position, direction)
            #Check if state should be changed
            #Enemy doesn't sees player or player is not in range
            if not self.sees_player(self.world.collider[self.world.player].center) or not self.point_in_radius(self.aggresion_range, players_position):
                #Set duration of idle state
                self.counter = 30
                self.current_action = self.cruise

class Level1_curse(AI):
    """Handles Level curse's AI.
    
    Spawns in random position projectiles in direction to player.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """

    def __init__(self, world, entity_ID, event_manager):
        """
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        AI.__init__(self, world, entity_ID, event_manager)
        #Set idle function for the AI
        self.current_action = self.idle
    
    def idle(self, event):
        """Idle, lasts ... frames long.
        
        No action happen here.

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            self.counter -= 1
            if self.counter == 0:
                self.counter = 60
                self.current_action = self.cast_curse

    def cast_curse(self, event):
        if isinstance(event, events.CollisionOccured):
            #If player collided
            if event.collider_ID == self.world.player:
                #And if collidee is a green cursed platform
                if hasattr(event.collidee, 'tags'):
                    tags = event.collidee.tags
                    if tags:
                        if "green" in tags:
                            #Cast curse
                            player_position = self.world.collider[self.world.player].center
                            spawn_attack_position = self.calculate_random_position_in_radius(player_position, 200, 300)
                            direction = [player_position[0] - spawn_attack_position[0],
                                         player_position[1] - spawn_attack_position[1]]
                            direction = calculate_octant(direction)
                            if direction[0] == 0 and direction[1] == 0:
                                #Direction (0,0) is not valid
                                direction = (1, 0)
                            self.attack(0, spawn_attack_position, direction)
                            self.current_action = self.idle

    def calculate_random_position_in_radius(self, point, min_distance, max_distance):
        radius = random_(min_distance, max_distance)
        vector = [1, 0]
        angle = random_(0, 360)
        vector = chaosparticle.get_rotated_vector(vector, angle)
        #Vector is rotated and normalized now
        #Scale and translate vector
        vector = [vector[0]*radius + point[0], vector[1]*radius + point[1]]
        vector = map(int, vector)
        return vector

class Level2_curse(AI):
    """Handles Level curse's AI.
    
    Spawns attack from the ground if player collides with this ground.

    :Attributes:
        - *event_manager* (:class:`events.EventManager`): event manager
        - *world* (:class:`gameWorld.GameWorld`): game world contains entities
        - *current_action* (function): current update function for AI
        - *entity_ID* (int): this AI belongs to this entity
    """

    def __init__(self, world, entity_ID, event_manager):
        """
        :param world: game world contains entities
        :type world: gameWorld.GameWorld
        """
        AI.__init__(self, world, entity_ID, event_manager)
        self.counter = list()
        self.time_till_attack = 30 # Delayed attack
        #Set idle function for the AI
        self.current_action = self.idle
        self.cast_pos = list() # needed to store position of curse
        self.sleep_reset = 60
        self.sleep = 0 # Only if sleep cooldown is over, collision is registered
    
    def idle(self, event):
        """Idle.
        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.CollisionOccured):
            if self.sleep == 0 and event.collider_ID == self.world.player:
                if hasattr(event.collidee, 'tags'):
                    tags = event.collidee.tags
                    if tags:
                        if "pink" in tags:
                            player_position = self.world.collider[self.world.player].center
                            #new_position = (event.collidee.center[0], event.collidee.center[1] - 32)
                            new_position = (player_position[0], event.collidee.center[1] - 32)
                            #self.cast_curse(new_position)                            
                            '''
                            # Avoid duplicate position:
                            if len(self.cast_pos)>0:
                                last_position = self.cast_pos[len(self.cast_pos)-1]
                                if not (last_position[0] == new_position[0] and last_position[1] == new_position[1]):
                                    print(new_position)
                                    self.cast_pos.append(new_position)
                                    self.counter.append(self.time_till_attack)
                            else:
                            '''
                            self.cast_pos.append(new_position)
                            self.counter.append(self.time_till_attack)
                            #Create animation, so player knows, where attack is casted
                            temp_eff = pygame.image.load(os.path.join('data', 'curse_pink_effect.png'))
                            eff_sprite = components.Appearance(temp_eff.convert_alpha(), 128, 128, [8], [self.time_till_attack])
                            eff_sprite.play_animation_till_end = True
                            eff_sprite.play_once = True
                            #eff_sprite.self_destruct = True
                            eff_sprite.rect.center = (new_position[0], new_position[1] + 42)
                            effect_ID = self.world.create_entity((eff_sprite, ))
                            self.sleep = self.sleep_reset
                            
        elif isinstance(event, events.TickEvent):
            if self.sleep > 0:
                self.sleep -= 1
            to_remove = list()
            for i in range(len(self.counter)):
                self.counter[i] -= 1
                if self.counter[i] == 0:
                    to_remove.append(i)
            for i in range(len(to_remove)):
                self.counter.pop(to_remove[i])
                position = self.cast_pos.pop(i)
                position = (position[0], position[1] + 12)
                self.cast_curse(position)
                         
    def cast_curse(self, position):
        direction = (0, -1)
        self.attack(0, position, direction)
