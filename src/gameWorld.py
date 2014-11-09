"""
.. module:: gameWorld
    :platform: Unix, Windows
    :synopsis: Container of all entities in game.
"""

import os
import pygame
import level
import components

class GameWorld(object):
    """ Container of all entities in game.

    :Attribute:
        - *screen* (pygame.Surface): reference to the game screen
        - *level* (level.Level): current level
        :Components:
            - *mask* (int list): contains a number equal the amount of components of the entity, index of the element is entities ID
            - *appearance* (dictionary ID : components.Apperance): animations and images
            - *collider* (dictionary ID : components.Collider): hitboxes
            - *velocity* (dictionary ID : float tuple): velocity for movable entities
            - *direction* (dictionary ID : tuple): aim and attack direction (das aendern, in den Player rein!!!)
            - *characters* (dictionary ID : ): enemies and player (das besser aufplitten ??!!)
            - *state* (dictionary ID : components.State): states of entities
            - *player* (int): ID of single player
    """

    def __init__(self, screen):
        """
        :param screen: game screen
        :type screen: python.Surface
        """
        self.level = level.Level()
        self.screen = screen

        #Components and entities
        self.mask = list()
        self.appearance = {}
        self.collider = {}
        self.velocity = {}
        self.direction = {}
        self.charakters = {}
        self.state = {}
        self.player = None
        self.attacks = list()
        
        #Create all game entities
        
        #Create characters
        #layer = self.level.tmx_data.getTileLayerByName("charakters")
        '''LayerWeite und Breite auslesen!! Sowie die Nummer'''
        for x in range(49):
            for y in range(49):
                tile = self.level.tmx_data.getTileProperties((x, y, 4))
                if tile:
                    if "type" in tile:
                        if tile["type"] == "player":
                            #Create player
                            #Players hitbox
                            coll = components.Collider(x*64, y*64, 50, 96)
                            vel = components.Velocity([0, 0])
                            #Create players animations
                            temp = pygame.image.load(os.path.join('data', 'char.png')).convert_alpha()
                            anim_list = [4, 10, 3]
                            anim_time_list = [240, 60, 44]
                            anim = components.Appearance(temp, 128, 128,
                                                         anim_list,
                                                         anim_time_list)
                            anim.rect.center = coll.center
                            player = components.Player(tile["name"], 0)
                            c = (coll, vel, anim, player, components.State())
                            self.player = self.create_entity(c)

                            #Now create the players orb
                            #It is created afterward, so orb will be
                            #displayed over players sprite
                            orb_direction = components.Direction([1, 0])
                            temp = pygame.image.load(os.path.join('data', 'orb.png'))
                            orb_sprite = components.Appearance(temp.convert_alpha())
                            c_orb = (orb_direction, orb_sprite)
                            orb_ID = self.create_entity(c_orb)
                            #Set orb ID
                            self.charakters[self.player].orb_ID = orb_ID
        #Create walls
        for wall in self.level.tmx_data.objects:
            coll = components.Collider(wall.x, wall.y, wall.width, wall.height)
            c = (coll,)
            self.create_entity(c)

    def create_particle_emitter(self, position):
        vel = components.Velocity(self.direction[self.charakters[self.player].orb_ID])
        #vel = [vel[0]*4, vel[1]*4]
        orb_sprite = pygame.image.load(os.path.join('data', 'orb.png'))
        #
        acceleration = [0, 0]
        life = 10
        amount = 5
        particle_emitter = components.Attack(self.player, 10, position,
                                             amount, orb_sprite, life,
                                             vel, acceleration)
        self.attacks.append(particle_emitter)

    def create_entity(self, c):
        """Adds an entity to the game world.
        
        :param c: all components of new entity
        :type c: components list
        :rtype: ID of the new entity
        """
        entity = self.get_empty_entity()
        for component in c:
            if isinstance(component, components.Collider):
                self.collider[entity] = component
            elif isinstance(component, components.Velocity):
                self.velocity[entity] = component
            elif isinstance(component, components.Appearance):
                self.appearance[entity] = component
            elif isinstance(component, components.Direction):
                self.direction[entity] = component
            elif isinstance(component, components.Player):
                self.charakters[entity] = component
            elif isinstance(component, components.State):
                self.state[entity] = component
        #Set amount of components of new entity
        self.mask[entity] = len(c)
        #Return ID of new entity
        return entity

    def get_empty_entity(self):
        """Gets not used index as an ID for new entity.
        
        :rtype: ID of an empty entity
        """
        for entity in range(len(self.mask)):
            #There is unused ID, if there are no components assigned
            if self.mask[entity] == 0:
                return entity
        #If mask isn't long enough, add new element
        entity = len(self.mask) 
        self.mask.append(0)
        return entity

    def destroy_entity(self, entity_ID):
        self.mask[entity_ID] = 0
        #Clear dictionaries
        if entity_ID in self.appearance:
            del self.appearance[entity_ID]
        if entity_ID in self.collider:
            del self.collider[entity_ID]
        if entity_ID in self.velocity:
            del self.velocity[entity_ID]
        if entity_ID in self.direction:
            del self.direction[entity_ID]
        if entity_ID in self.charakters:
            del self.charakters[entity_ID]
        if entity_ID in self.state:
            del self.state[entity_ID]

