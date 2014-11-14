"""
.. module:: gameworld
    :platform: Unix, Windows
    :synopsis: Container of all entities in game.
"""

import os
import pygame
import level
import components
import chaosparticle

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
            - *direction* (dictionary ID : tuple): aim and attacks direction (das aendern, in den Player rein!!!)
            - *characters* (dictionary ID : ): enemies and player (das besser aufplitten ??!!)
            - *state* (dictionary ID : components.State): states of entities
            - *attacks* (dictionary ID : components.Attack): attacks of the charakters
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
        self.attacks = {}
        self.player = None
        
        #Create all game entities
        
        #Create characters
        #layer = self.level.tmx_data.getTileLayerByName("charakters")
        '''LayerWeite und Breite auslesen!! Sowie die Nummer'''
        #Temp list to store fields
        fields = list()
        for x in range(49):
            for y in range(49):
                tile = self.level.tmx_data.getTileProperties((x, y, 4))
                if tile:
                    if "type" in tile:
                        if tile["type"] == "player":
                            #Create player
                            position = (x*64+32, y*64+32)
                            self.create_player(position)
                tile = self.level.tmx_data.getTileProperties((x, y, 3))
                if tile:
                    if "type" in tile:
                        if tile["type"] == "field":
                            #Add fields
                            mass = int(tile["mass"])
                            position = (x*64+32, y*64+32)
                            fields.append(chaosparticle.Field(position, mass))
        #Characters and their attacks are created, so fields can be added
        for field in fields:
            self.create_field(field.position, field.mass)
        #Create walls
        for wall in self.level.tmx_data.objects:
            coll = components.Collider(wall.x, wall.y, wall.width, wall.height)
            c = (coll,)
            self.create_entity(c)

    def create_field(self, position, mass):
        """Adds field to all attacks.
        
        :param position: position of the field
        :type postion: 2d list
        :param mass: mass
        :type mass: int
        """
        for attacks in self.attacks.itervalues():
            for attack in attacks:
                attack.add_field(chaosparticle.Field(position, mass))

    def create_player(self, position):
        """Create player.
        
        :param position: position where player is created
        :type position: 2d list
        """
        #Players hitbox, it ist 50 pixel width and 96 pixel height
        coll = components.Collider(position[0], position[1], 50, 96)
        vel = components.Velocity([0, 0])
        #Create players animations
        temp = pygame.image.load(os.path.join('data', 'char.png')).convert_alpha()
        anim_list = [4, 10, 3]
        anim_time_list = [240, 60, 44]
        anim = components.Appearance(temp, 128, 128, anim_list, anim_time_list)
        anim.rect.center = coll.center
        player = components.Player(0)
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
        #Create players attacks
        #attack 1
        damage = 10
        position = coll.center
        particle_emitter = components.Attack(self.player, damage, 30, position,
                                             25, temp, 120,
                                             self.direction[orb_ID], [0, 0], 10)
        attack_list = list()
        attack_list.append(particle_emitter)
        self.add_component_to_entity(self.player, attack_list)

    def add_component_to_entity(self, entity_ID, component):
        if isinstance(component, components.Collider):
            self.collider[entity_ID] = component
        elif isinstance(component, components.Velocity):
            self.velocity[entity_ID] = component
        elif isinstance(component, components.Appearance):
            self.appearance[entity_ID] = component
        elif isinstance(component, components.Direction):
            self.direction[entity_ID] = component
        elif isinstance(component, components.Player):
            self.charakters[entity_ID] = component
        elif isinstance(component, components.State):
            self.state[entity_ID] = component
        elif isinstance(component, list):
            if isinstance(component[0], components.Attack):
                self.attacks[entity_ID] = component
        #Increase amount of components of the entity
        self.mask[entity_ID] += 1

    def create_entity(self, c):
        """Adds an entity to the game world.
        
        :param c: all components of new entity
        :type c: components list
        :rtype: ID of the new entity
        """
        entity = self.get_empty_entity()
        for component in c:
            self.add_component_to_entity(entity, component)
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

'''
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
'''
