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
import ai

import quadTree

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
            - *attacks* (dictionary ID : components.Attack): attacks of the characters
            - *player* (int): ID of single player
            - *ai* (dictionary ID : ai): all AI for  enemies
    """

    def __init__(self, screen, event_manager):
        """
        :param screen: game screen
        :type screen: python.Surface
        :param event_managere: event manager
        :type event_manager: events.EventManager
        """
        self.level = level.Level()
        self.screen = screen
        self.event_manager = event_manager

        #Components and entities
        self.mask = list()
        self.appearance = {}
        self.collider = {}
        self.velocity = {}
        self.direction = {}
        self.players = {}
        self.state = {}
        self.attacks = {}
        self.player = None
        self.ai = {}
        self.tags = {}
        self.hp = {}
        
        #Create all game entities
        
        #Create characters
        #layer = self.level.tmx_data.getTileLayerByName("players")
        '''LayerWeite und Breite auslesen!! Sowie die Nummer'''
        #Temp list
        fields = list()
        walls = list()
        #Get layer width and height in tiles
        layer_width = len(self.level.tmx_data.tilelayers[0].data)
        layer_height = len(self.level.tmx_data.tilelayers[0].data[0])
        for layer_index in range(len(self.level.tmx_data.tilelayers)):
            for x in range(layer_width):
                for y in range(layer_height):
                    if self.level.tmx_data.tilelayers[layer_index].name == "characters":
                        tile = self.level.tmx_data.getTileProperties((x, y, layer_index))
                        if tile:
                            if "type" in tile:
                                if tile["type"] == "enemy":
                                    #Create enemies
                                    position = (x*64+32, y*64+32)
                                    self.create_enemy(position)
                                elif tile["type"] == "player":
                                    #Create player
                                    position = (x*64+32, y*64+32)
                                    self.create_player(position)
                    if self.level.tmx_data.tilelayers[layer_index].name == "decoration front":
                        tile = self.level.tmx_data.getTileProperties((x, y, layer_index))
                        if tile:
                            if "type" in tile:
                                if tile["type"] == "field":
                                    #Add fields
                                    mass = int(tile["mass"])
                                    position = (x*64+32, y*64+32)
                                    fields.append(chaosparticle.Field(position, mass))
                    #Create walls
                    if self.level.tmx_data.tilelayers[layer_index].name == "walls":
                        tile = self.level.tmx_data.getTileImage(x, y, layer_index)
                        tile_properties = self.level.tmx_data.getTileProperties((x, y, layer_index))
                        if tile:
                            tags = list()
                            if tile_properties:
                                if "type" in tile_properties:
                                    if tile_properties["type"] == "corner":
                                        #Tile is a corner
                                        tags.append("corner")
                            coll = components.Collider(x*64, y*64, 64, 64, tags)
                            walls.append(coll)
        #Characters and their attacks are created, so fields can be added
        for field in fields:
            self.create_field(field.position, field.mass)
        #Quad Tree
        self.tree = quadTree.QuadTree(walls)

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
        #Create players hp gui
        temp = pygame.image.load(os.path.join('data', 'hp.png')).convert_alpha()
        hp = components.Health(150, 3, temp)
        c_hp = (hp, hp.current_image)
        hp_ID = self.create_entity(c_hp)
        #Players hitbox, it is 50 pixel width and 96 pixel height
        coll = components.Collider(position[0], position[1], 50, 96)
        vel = components.Velocity([0, 0])
        #Create players animations
        temp = pygame.image.load(os.path.join('data', 'char.png')).convert_alpha()
        anim_list = [4, 10, 3]
        anim_time_list = [240, 60, 44]
        anim = components.Appearance(temp, 128, 128, anim_list, anim_time_list)
        anim.rect.center = coll.center
        direction = components.Direction([1, 0])
        player = components.Player(0, hp_ID, )
        c = (direction, coll, vel, anim, player, components.State())
        self.player = self.create_entity(c)
        #Now create the players orb
        #It is created afterward, so orb will be
        #displayed over players sprite
        temp = pygame.image.load(os.path.join('data', 'orb.png'))
        orb_sprite = components.Appearance(temp.convert_alpha())
        c_orb = (orb_sprite,)
        orb_ID = self.create_entity(c_orb)
        #Set orb ID
        self.players[self.player].orb_ID = orb_ID
        #Create players attacks
        #attack 1
        damage = 10
        position = coll.center
        particle_emitter = components.Attack(self.player, damage, 30, position,
                                             5, temp, 60,
                                             self.direction[self.player], [0, 0], 15)
        attack_list = list()
        attack_list.append(particle_emitter)
        self.add_component_to_entity(self.player, attack_list)

    def create_enemy(self, position):
        """Create an enemy.
        
        :param position: position where enemy is created
        :type position: 2d list
        """
        #Enemy's hitbox, it is 50 pixel width and 96 pixel height
        coll = components.Collider(position[0], position[1], 50, 96)
        vel = components.Velocity([0, 0])
        #Create enemy's animations
        temp = pygame.image.load(os.path.join('data', 'char.png')).convert_alpha()
        anim_list = [4, 10, 3]
        anim_time_list = [240, 60, 44]
        anim = components.Appearance(temp, 128, 128, anim_list, anim_time_list)
        anim.rect.center = coll.center
        direction = components.Direction([1, 0])
        c = (coll, direction, vel, anim, components.State())
        enemy_ID = self.create_entity(c)

        enemy_AI = ai.AI_1(self.event_manager, self, enemy_ID)
        self.add_component_to_entity(enemy_ID, enemy_AI)

        projectile_image = pygame.image.load(os.path.join('data', 'orb.png'))
        #Create enemies attacks
        #attack 1
        damage = 10
        position = coll.center
        particle_emitter = components.Attack(enemy_ID, damage, 30, position,
                                             3, projectile_image, 60,
                                             self.direction[enemy_ID], [0, 0], 15)
        attack_list = list()
        attack_list.append(particle_emitter)
        self.add_component_to_entity(enemy_ID, attack_list)

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
            self.players[entity_ID] = component
        elif isinstance(component, components.State):
            self.state[entity_ID] = component
        elif isinstance(component, list):
            if isinstance(component[0], components.Attack):
                self.attacks[entity_ID] = component
        elif isinstance(component, ai.AI):
            self.ai[entity_ID] = component
        elif isinstance(component, components.Health):
            self.hp[entity_ID] = component
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
        if entity_ID in self.players:
            del self.players[entity_ID]
        if entity_ID in self.state:
            del self.state[entity_ID]
'''
