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
import collectible

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
        self.attacks = {}
        self.player = None
        self.ai = {}
        self.tags = {}
        self.hp = {}
        self.collectibles = {}
        
        self.inactive_entities = list()
        self.to_remove = list()
        
        #Create all game entities
        walls = list()
        #Get layer width and height in tiles
        layer_width = len(self.level.tmx_data.layers[0].data)
        layer_height = len(self.level.tmx_data.layers[0].data[0])
        for layer_index in range(len(self.level.tmx_data.layers)):
            #BUG? pyTMX reads from top to down, then from left to right
            #So: y in range(layer_width) and x in range (layer_heigt)
            for y in range(layer_width):
                for x in range(layer_height):
                    ####
                    tile_properties = self.level.tmx_data.get_tile_properties(x, y, layer_index)
                    if self.level.tmx_data.layers[layer_index].name == "characters":
                        if tile_properties:
                            if "type" in tile_properties:
                                if tile_properties["type"] == "enemy":
                                    position = (x*64+32, y*64+32)
                                    if "max_hp" in tile_properties:
                                        hp = int(tile_properties["max_hp"])
                                    if "max_x_vel" in tile_properties:
                                        max_x_vel = int(tile_properties["max_x_vel"])
                                    if "max_y_vel" in tile_properties:
                                        max_y_vel = int(tile_properties["max_y_vel"])
                                    #Attack related:
                                    if "att_1_damage" in tile_properties:
                                        damage = int(tile_properties["att_1_damage"])
                                    if "att_1_stun" in tile_properties:
                                        stun = int(tile_properties["att_1_stun"])
                                    if "att_1_cooldown" in tile_properties:
                                        cooldown = int(tile_properties["att_1_cooldown"])
                                    if "att_1_projectile_amount" in tile_properties:
                                        proj = int(tile_properties["att_1_projectile_amount"])
                                    if "att_1_projectile_lifetime" in tile_properties:
                                        proj_life = int(tile_properties["att_1_projectile_lifetime"])
                                    if "att_1_spread_angle" in tile_properties:
                                        spread = int(tile_properties["att_1_spread_angle"])
                                    if "ai" in tile_properties:
                                        ai_ID = tile_properties["ai"]
                                    #Create enemy attacks
                                    #Attack 1:
                                    projectile_image = "proj.png"
                                    particle_emitter = self.create_attack(position, damage, stun,
                                                                          cooldown, proj, projectile_image,
                                                                          proj_life, [0, 1], [0,0],
                                                                          spread)
                                    attack_list = list()
                                    attack_list.append(particle_emitter)
                                    self.create_enemy(position, hp, max_x_vel, max_y_vel,
                                                      attack_list, ai_ID)

                                elif tile_properties["type"] == "player":
                                    position = (x*64+32, y*64+32)
                                    if "max_hp" in tile_properties:
                                        hp = int(tile_properties["max_hp"])
                                    if "max_x_vel" in tile_properties:
                                        max_x_vel = int(tile_properties["max_x_vel"])
                                    if "max_y_vel" in tile_properties:
                                        max_y_vel = int(tile_properties["max_y_vel"])
                                    #Attack related:
                                    if "att_1_damage" in tile_properties:
                                        damage = int(tile_properties["att_1_damage"])
                                    if "att_1_stun" in tile_properties:
                                        stun = int(tile_properties["att_1_stun"])
                                    if "att_1_cooldown" in tile_properties:
                                        cooldown = int(tile_properties["att_1_cooldown"])
                                    if "att_1_projectile_amount" in tile_properties:
                                        proj = int(tile_properties["att_1_projectile_amount"])
                                    if "att_1_projectile_lifetime" in tile_properties:
                                        proj_life = int(tile_properties["att_1_projectile_lifetime"])
                                    if "att_1_spread_angle" in tile_properties:
                                        spread = int(tile_properties["att_1_spread_angle"])
                                    #Create players attacks
                                    #Attack 1:
                                    effect_ID = self.create_attack_effect('char_attack1_effect.png',
                                                                          250, 250, 8, 30)
                                    projectile_image = "proj.png"
                                    particle_emitter = self.create_attack(position, damage, stun,
                                                                          cooldown, proj, projectile_image,
                                                                          proj_life, [0,1], [0,0],
                                                                          spread, effect_ID)
                                    attack_list = list()
                                    attack_list.append(particle_emitter)
                                    self.create_player(position, hp, max_x_vel, max_y_vel,
                                                       attack_list)

                                elif tile_properties["type"] == "heal_potion":
                                    #Add fields
                                    recovery = int(tile_properties["recovery"])
                                    tags = list()
                                    tags.append("heal_potion")
                                    collider = components.Collider(x*64, y*64, 64, 64, tags)
                                    temp = pygame.image.load(os.path.join('data', 'heal_pot.png'))
                                    heal_sprite = components.Appearance(temp.convert_alpha())
                                    heal_sprite.rect.center = collider.center
                                    heal_pot = collectible.HealPotion(self, self.event_manager, recovery)
                                    colle_ID = self.create_entity((heal_sprite, heal_pot, collider))
                                    heal_pot.entity_ID = colle_ID
                                elif tile_properties["type"] == "skill_up":
                                    collider = components.Collider(x*64, y*64, 64, 64)
                                    temp = pygame.image.load(os.path.join('data', 'skill_pot.png'))
                                    skillup_sprite = components.Appearance(temp.convert_alpha())
                                    skillup_sprite.rect.center = collider.center
                                    skillup_pot = collectible.SkillUp(self, self.event_manager)
                                    colle_ID = self.create_entity((skillup_sprite, skillup_pot, collider))
                                    skillup_pot.entity_ID = colle_ID
                                elif tile_properties["type"] == "portal":
                                    x_pos = int(tile_properties["x"])
                                    y_pos = int(tile_properties["y"])
                                    x_pos, y_pos = x_pos*64+32, y_pos*64+32
                                    collider = components.Collider(x*64, y*64, 64, 64)
                                    temp = pygame.image.load(os.path.join('data', 'portal.png'))
                                    portal_sprite = components.Appearance(temp.convert_alpha())
                                    portal_sprite.rect.center = collider.center
                                    portal = collectible.Portal(self, self.event_manager, x_pos, y_pos)
                                    colle_ID = self.create_entity((portal_sprite, portal, collider))
                                    portal.entity_ID = colle_ID
                                                                 
                    #Create walls
                    if self.level.tmx_data.layers[layer_index].name == "walls":
                        tile = self.level.tmx_data.get_tile_image(x, y, layer_index)
                        if tile:
                            tags = list()
                            if tile_properties:
                                if "type" in tile_properties:
                                    if tile_properties["type"] == "corner":
                                        #Tile is a corner
                                        tags.append("corner")
                            coll = components.Collider(x*64, y*64, 64, 64, tags)
                            walls.append(coll)
        #Create Level curse:
        #---
        damage = 10
        stun = 10
        cooldown = 50
        position = [0,0]
        
        temp_eff = pygame.image.load(os.path.join('data', 'curse_green_effect.png'))
        eff_sprite = components.Appearance(temp_eff.convert_alpha(), 170, 170, [5], [40])
        eff_sprite.play_animation_till_end = True
        eff_sprite.play_once = True
        effect_ID = self.create_entity((eff_sprite, ))
        curse_AI = ai.Level1_curse(self, 0, self.event_manager)
        curse_ID = self.create_entity((curse_AI, ))
        curse_AI.entity_ID = curse_ID 
        particle_emitter = components.Attack(self, damage, stun, cooldown, position,
                                             1, 'proj.png', 60,
                                             [1, 0], [0, 0], 15, effect_ID)
        attack_list = list()
        attack_list.append(particle_emitter)
        self.add_component_to_entity(curse_ID, attack_list)
        #---
        #Quad Tree
        self.tree = quadTree.QuadTree(walls)

    def create_attack(self, position, damage, stun, cooldown, proj_amount,
                      projectile_image, projlife, velocity, accel, spread, effect_ID=None):
        """
        :param position: position of attack
        :type position: 2D list 
        :param damage: damage
        :type damage: int
        :param stun: stun inflicted by attack in frames
        :type stun: int
        :param cooldown: cooldown in frames
        :type cooldown: int
        :param proj_amount: amount of projectiles pro attack 
        :type proj_amount: int
        :param projectile_image: image representation of projectile 
        :type projectile_image:
        :param projlife: projectile lifetime in frames
        :type projlife: int
        :param velocity: velocity
        :type velocity: 2d list
        :param accel: acceleration
        :type accel: 2d list
        :param spread: spread angle
        :type spread: int
        :param effect_ID: ID of previously created effect representation
        :type effect_ID: int
        :rtype: created Attack
        """
        if not damage:
            damage = 10
        if not stun:
            stun = 30
        if not cooldown:
            cooldown = 30
        if not proj_amount:
            proj_amount = 1
        if not projlife:
            projlife = 60
        if not spread:
            spread = 15
        attack = components.Attack(self, damage, stun, cooldown, position,
                                   proj_amount, projectile_image, projlife,
                                   velocity, [0, 0], spread, effect_ID)
        return attack

    def create_attack_effect(self, image_name, sprite_w, sprite_h, frames, time):
        temp_eff = pygame.image.load(os.path.join('data', image_name))
        eff_sprite = components.Appearance(temp_eff.convert_alpha(), sprite_w, sprite_h, [frames], [time])
        eff_sprite.play_once = True
        eff_sprite.play_animation_till_end = True
        c_eff = (eff_sprite,)
        effect_ID = self.create_entity(c_eff)
        return effect_ID

    def create_player(self, position, max_hp, max_x_vel, max_y_vel, attack_list):
        
        """Create player.
        
        :param position: position where player is created
        :type position: 2d list
        """
        #Create players hp gui
        temp = pygame.image.load(os.path.join('data', 'hp.png')).convert_alpha()
        hp = components.Health(max_hp, 8, temp)
        c_hp = (hp, hp.current_image)
        hp_ID = self.create_entity(c_hp)
        #Players hitbox, it is 50 pixel width and 96 pixel height
        coll = components.Collider(position[0], position[1], 50, 96)
        vel = components.Velocity(0, 0, max_x_vel, max_y_vel)
        #Create players animations
        temp = pygame.image.load(os.path.join('data', 'char.png')).convert_alpha()
        anim_list = [4, 10, 8, 8, 2, 2]
        anim_time_list = [240, 50, 44, 60, 30, 44]
        anim = components.Appearance(temp, 128, 128, anim_list, anim_time_list)
        anim.rect.center = coll.center
        direction = components.Direction([1, 0])
        player = components.Player(0, hp_ID, )
        c = (direction, coll, vel, anim, player)
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
        self.add_component_to_entity(self.player, attack_list)

    def create_enemy(self, position, max_hp, max_x_vel, max_y_vel, attack_list, ai_ID):
        """Create an enemy.
        
        :param position: position where enemy is created
        :type position: 2d list
        """
        #Enemy's hitbox, it is 50 pixel width and 96 pixel height
        coll = components.Collider(position[0], position[1], 50, 96)
        vel = components.Velocity(0, 0, max_x_vel, max_y_vel)
        #Create enemy's animations
        temp = pygame.image.load(os.path.join('data', 'enemy_green_1.png')).convert_alpha()
        anim_list = [2, 10, 4, 8, 2, 1]
        anim_time_list = [240, 60, 44, 120, 10, 10]
        anim = components.Appearance(temp, 128, 128, anim_list, anim_time_list)
        anim.rect.center = coll.center
        direction = components.Direction([1, 0])
        hp = components.Health(max_hp)
        c = (coll, direction, vel, anim, hp)
        enemy_ID = self.create_entity(c)

        if ai_ID == "green_1":
            enemy_AI = ai.AI_1(self, enemy_ID, self.event_manager)
        self.add_component_to_entity(enemy_ID, enemy_AI)
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
        elif isinstance(component, list):
            if isinstance(component[0], components.Attack):
                self.attacks[entity_ID] = component
        elif isinstance(component, ai.AI):
            self.ai[entity_ID] = component
        elif isinstance(component, components.Health):
            self.hp[entity_ID] = component
        elif isinstance(component, collectible.Collectible):
            self.collectibles[entity_ID] = component
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

    def active_entity(self, entity_ID):        
        return not entity_ID in self.inactive_entities

    def deactivate_entity(self, entity_ID):
        if not entity_ID in self.inactive_entities:
            self.inactive_entities.append(entity_ID)

    def destroy_entity(self, entity_ID):
        #Clear mask, this entity has no components more
        self.mask[entity_ID] = 0
        #Clear dictionaries
        if entity_ID in self.collider:
            del self.collider[entity_ID]
        if entity_ID in self.velocity:
            del self.velocity[entity_ID]
        if entity_ID in self.appearance:
            del self.appearance[entity_ID]
        if entity_ID in self.direction:
            del self.direction[entity_ID]
        if entity_ID in self.players:
            del self.players[entity_ID]
        if entity_ID in self.attacks:
            del self.attacks[entity_ID]
        if entity_ID in self.ai:
            self.event_manager.unregister_listener(self.ai[entity_ID])
            del self.ai[entity_ID]
        if entity_ID in self.hp:
            del self.hp[entity_ID]
        if entity_ID in self.collectibles:
            del self.collectibles[entity_ID]

    def reset_the_world(self):
        for entity_ID in range(len(self.mask)):
            #No point to reset indestructible walls.
            #Walls are in qudtree
            self.destroy_entity(entity_ID)
        #Reload Objects
        layer_width = len(self.level.tmx_data.layers[0].data)
        layer_height = len(self.level.tmx_data.layers[0].data[0])
        layer_index = len(self.level.tmx_data.layers)-1
        self.inactive_entities = list()
        #BUG? pyTMX reads from top to down, then fom left to right
        #So: y in range(layer_width) ans x in range (layer_heigt)
        for y in range(layer_width):
            for x in range(layer_height):
                #####
                tile_properties = self.level.tmx_data.get_tile_properties(x, y, layer_index)
                if self.level.tmx_data.layers[layer_index].name == "characters":
                    if tile_properties:
                        if "type" in tile_properties:
                            if tile_properties["type"] == "enemy":
                                position = (x*64+32, y*64+32)
                                if "max_hp" in tile_properties:
                                    hp = int(tile_properties["max_hp"])
                                if "max_x_vel" in tile_properties:
                                    max_x_vel = int(tile_properties["max_x_vel"])
                                if "max_y_vel" in tile_properties:
                                    max_y_vel = int(tile_properties["max_y_vel"])
                                #Attack related:
                                if "att_1_damage" in tile_properties:
                                    damage = int(tile_properties["att_1_damage"])
                                if "att_1_stun" in tile_properties:
                                    stun = int(tile_properties["att_1_stun"])
                                if "att_1_cooldown" in tile_properties:
                                    cooldown = int(tile_properties["att_1_cooldown"])
                                if "att_1_projectile_amount" in tile_properties:
                                    proj = int(tile_properties["att_1_projectile_amount"])
                                if "att_1_projectile_lifetime" in tile_properties:
                                    proj_life = int(tile_properties["att_1_projectile_lifetime"])
                                if "att_1_spread_angle" in tile_properties:
                                    spread = int(tile_properties["att_1_spread_angle"])
                                if "ai" in tile_properties:
                                    ai_ID = tile_properties["ai"]
                                #Create enemy attacks
                                #Attack 1:
                                projectile_image = "proj.png"
                                particle_emitter = self.create_attack(position, damage, stun,
                                                                      cooldown, proj, projectile_image,
                                                                      proj_life, [0, 1], [0,0],
                                                                      spread)
                                attack_list = list()
                                attack_list.append(particle_emitter)
                                self.create_enemy(position, hp, max_x_vel, max_y_vel,
                                                  attack_list, ai_ID)

                            elif tile_properties["type"] == "player":
                                position = (x*64+32, y*64+32)
                                if "max_hp" in tile_properties:
                                    hp = int(tile_properties["max_hp"])
                                if "max_x_vel" in tile_properties:
                                    max_x_vel = int(tile_properties["max_x_vel"])
                                if "max_y_vel" in tile_properties:
                                    max_y_vel = int(tile_properties["max_y_vel"])
                                #Attack related:
                                if "att_1_damage" in tile_properties:
                                    damage = int(tile_properties["att_1_damage"])
                                if "att_1_stun" in tile_properties:
                                    stun = int(tile_properties["att_1_stun"])
                                if "att_1_cooldown" in tile_properties:
                                    cooldown = int(tile_properties["att_1_cooldown"])
                                if "att_1_projectile_amount" in tile_properties:
                                    proj = int(tile_properties["att_1_projectile_amount"])
                                if "att_1_projectile_lifetime" in tile_properties:
                                    proj_life = int(tile_properties["att_1_projectile_lifetime"])
                                if "att_1_spread_angle" in tile_properties:
                                    spread = int(tile_properties["att_1_spread_angle"])
                                #Create players attacks
                                #Attack 1:
                                effect_ID = self.create_attack_effect('char_attack1_effect.png',
                                                                      250, 250, 8, 30)
                                projectile_image = "proj.png"
                                particle_emitter = self.create_attack(position, damage, stun,
                                                                      cooldown, proj, projectile_image,
                                                                      proj_life, [0,1], [0,0],
                                                                      spread, effect_ID)
                                attack_list = list()
                                attack_list.append(particle_emitter)
                                self.create_player(position, hp, max_x_vel, max_y_vel,
                                                   attack_list)

                            elif tile_properties["type"] == "heal_potion":
                                #Add fields
                                recovery = int(tile_properties["recovery"])
                                tags = list()
                                tags.append("heal_potion")
                                collider = components.Collider(x*64, y*64, 64, 64, tags)
                                temp = pygame.image.load(os.path.join('data', 'heal_pot.png'))
                                heal_sprite = components.Appearance(temp.convert_alpha())
                                heal_sprite.rect.center = collider.center
                                heal_pot = collectible.HealPotion(self, self.event_manager, recovery)
                                colle_ID = self.create_entity((heal_sprite, heal_pot, collider))
                                heal_pot.entity_ID = colle_ID
                            elif tile_properties["type"] == "skill_up":
                                collider = components.Collider(x*64, y*64, 64, 64)
                                temp = pygame.image.load(os.path.join('data', 'skill_pot.png'))
                                skillup_sprite = components.Appearance(temp.convert_alpha())
                                skillup_sprite.rect.center = collider.center
                                skillup_pot = collectible.SkillUp(self, self.event_manager)
                                colle_ID = self.create_entity((skillup_sprite, skillup_pot, collider))
                                skillup_pot.entity_ID = colle_ID
                            elif tile_properties["type"] == "portal":
                                x_pos = int(tile_properties["x"])
                                y_pos = int(tile_properties["y"])
                                x_pos, y_pos = x_pos*64+32, y_pos*64+32
                                collider = components.Collider(x*64, y*64, 64, 64)
                                temp = pygame.image.load(os.path.join('data', 'portal.png'))
                                portal_sprite = components.Appearance(temp.convert_alpha())
                                portal_sprite.rect.center = collider.center
                                portal = collectible.Portal(self, self.event_manager, x_pos, y_pos)
                                colle_ID = self.create_entity((portal_sprite, portal, collider))
                                portal.entity_ID = colle_ID
        #Create Level curse:
        #---
        damage = 10
        stun = 10
        cooldown = 50
        position = [0,0]
        
        temp_eff = pygame.image.load(os.path.join('data', 'curse_green_effect.png'))
        eff_sprite = components.Appearance(temp_eff.convert_alpha(), 170, 170, [5], [40])
        eff_sprite.play_animation_till_end = True
        eff_sprite.play_once = True
        effect_ID = self.create_entity((eff_sprite, ))
        curse_AI = ai.Level1_curse(self, 0, self.event_manager)
        curse_ID = self.create_entity((curse_AI, ))
        curse_AI.entity_ID = curse_ID 
        particle_emitter = components.Attack(self, damage, stun, cooldown, position,
                                             1, 'proj.png', 60,
                                             [1, 0], [0, 0], 15, effect_ID)
        attack_list = list()
        attack_list.append(particle_emitter)
        self.add_component_to_entity(curse_ID, attack_list)
        ###
        