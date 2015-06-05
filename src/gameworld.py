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
                            self.create_game_object(x, y, tile_properties)                                
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
                                    if tile_properties["type"] == "deadly":
                                        #Deadly tile, instant death on player collision
                                        tags.append("deadly")
                                if "curse" in tile_properties:
                                    if tile_properties["curse"] == "green":
                                        tags.append("green")
                                    if tile_properties["curse"] == "pink":
                                        tags.append("pink")
                            coll = components.Collider(x*64, y*64, 64, 64, tags)
                            walls.append(coll)
        self.create_curse()
        #---
        #Quad Tree
        self.tree = quadTree.QuadTree(walls)

    def create_curse(self):
        #Create Level curse
        # GREEN
        damage = 10
        stun = 10
        cooldown = 50
        position = [0,0]
        '''
        temp_eff = pygame.image.load(os.path.join('data', 'curse_green_effect.png'))
        eff_sprite = components.Appearance(temp_eff.convert_alpha(), 114, 128, [8], [47])
        eff_sprite.play_animation_till_end = True
        eff_sprite.play_once = True
        effect_ID = self.create_entity((eff_sprite, ))
        '''
        effect_ID = self.create_attack_effect('curse_green_effect.png', 114, 128, 8, 47)
        curse_AI = ai.Level1_curse(self, 0, self.event_manager)
        curse_ID = self.create_entity((curse_AI, ))
        curse_AI.entity_ID = curse_ID
        #Create projectile image
        proj_image = "projectile_fly_orange.png"
        proj_anim_list = [4, 4]
        proj_anim_time_list = [37, 13]
        proj_width = 50
        proj_height = 50
        proj_life = 60
        speed = 3
        particle_emitter = components.Attack(self, damage, stun, cooldown, position,
                                             1, proj_image, proj_anim_list, proj_anim_time_list,
                                             proj_width, proj_height, proj_life,
                                             speed, [0, 0], 15, effect_ID)
        attack_list = list()
        attack_list.append(particle_emitter)
        self.add_component_to_entity(curse_ID, attack_list)

        # PINK
        damage = 10
        stun = 27
        cooldown = 0
        position = [0,0]
        # Other effect for this curse is set in ai.py
        effect_ID2 = self.create_attack_effect('tentakel.png', 60, 100, 9, 60)
        curse_AI2 = ai.Level2_curse(self, 0, self.event_manager)
        curse_ID2 = self.create_entity((curse_AI2, ))
        curse_AI2.entity_ID = curse_ID2
        #Create projectile image
        proj_image = "pink_proj.png"
        proj_anim_list = [2, 2]
        proj_anim_time_list = [47, 10]
        proj_width = 32
        proj_height = 32
        speed = 2
        proj_life = 33 
        particle_emitter = components.Attack(self, damage, stun, cooldown, position,
                                             1, proj_image, proj_anim_list, proj_anim_time_list,
                                             proj_width, proj_height, proj_life,
                                             speed, [0, 0], 15, effect_ID2)
        particle_emitter.piercing = True
        attack_list = list()
        attack_list.append(particle_emitter)
        self.add_component_to_entity(curse_ID2, attack_list)

    def create_game_object(self, x, y, tile_properties):
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
                #Create enemy attacks
                attack_list = list()
                #Attack 1:
                if "att_1_damage" in tile_properties:
                    damage1 = int(tile_properties["att_1_damage"])
                if "att_1_stun" in tile_properties:
                    stun1 = int(tile_properties["att_1_stun"])
                if "att_1_cooldown" in tile_properties:
                    cooldown1 = int(tile_properties["att_1_cooldown"])
                if "att_1_projectile_amount" in tile_properties:
                    proj1 = int(tile_properties["att_1_projectile_amount"])
                if "att_1_projectile_lifetime" in tile_properties:
                    proj_life1 = int(tile_properties["att_1_projectile_lifetime"])
                if "att_1_spread_angle" in tile_properties:
                    spread1 = int(tile_properties["att_1_spread_angle"])
                if "att_1_projectile_speed" in tile_properties:
                    proj_speed1 = int(tile_properties["att_1_projectile_speed"])
                if "ai" in tile_properties:
                    ai_ID = tile_properties["ai"]
                if "att_1_pierce" in tile_properties:
                    att1_pierce = tile_properties["att_1_pierce"] == "1"
                #Create projectile image
                if ai_ID == "green_1":
                    proj_image = "projectile_fly_green.png"
                    proj_anim_list = [2, 2]
                    proj_anim_time_list = [28, 13]
                    proj_width = 40
                    proj_height = 40
                elif ai_ID == "pink_1":
                    proj_image = "pink_proj.png"
                    proj_anim_list = [2, 2]
                    proj_anim_time_list = [50, 13]
                    proj_width = 32
                    proj_height = 32
                elif ai_ID == "pink_boss":
                    proj_image = "pink_proj.png"
                    proj_anim_list = [2, 2]
                    proj_anim_time_list = [50, 13]
                    proj_width = 32
                    proj_height = 32
                particle_emitter1 = self.create_attack(position, damage1, stun1,
                                                      cooldown1, proj1, proj_image,
                                                      proj_anim_list, proj_anim_time_list,
                                                      proj_width, proj_height,
                                                      proj_life1, proj_speed1, [0,0],
                                                      spread1)
                particle_emitter1.piercing = att1_pierce
                attack_list.append(particle_emitter1)
                #Attack 2
                damage2 = None
                if "att_2_damage" in tile_properties:
                    damage2 = int(tile_properties["att_2_damage"])
                if "att_2_stun" in tile_properties:
                    stun2 = int(tile_properties["att_2_stun"])
                if "att_2_cooldown" in tile_properties:
                    cooldown2 = int(tile_properties["att_2_cooldown"])
                if "att_2_projectile_amount" in tile_properties:
                    proj2 = int(tile_properties["att_2_projectile_amount"])
                if "att_2_projectile_lifetime" in tile_properties:
                    proj_life2 = int(tile_properties["att_2_projectile_lifetime"])
                if "att_2_spread_angle" in tile_properties:
                    spread2 = int(tile_properties["att_2_spread_angle"])
                if "att_2_projectile_speed" in tile_properties:
                    proj_speed2 = int(tile_properties["att_2_projectile_speed"])
                if "att_2_pierce" in tile_properties:
                    att2_pierce = tile_properties["att_2_pierce"] == "1"
                #Create projectile image
                if ai_ID == "pink_boss":
                    proj_image = "pink_proj.png"
                    proj_anim_list = [2, 2]
                    proj_anim_time_list = [50, 13]
                    proj_width = 32
                    proj_height = 32
                if damage2: #Attack exists
                    particle_emitter2 = self.create_attack(position, damage2, stun2,
                                                          cooldown2, proj2, proj_image,
                                                          proj_anim_list, proj_anim_time_list,
                                                          proj_width, proj_height,
                                                          proj_life2, proj_speed2, [0,0],
                                                          spread2)
                    particle_emitter2.piercing = att2_pierce
                    attack_list.append(particle_emitter2)
                #Attack 3
                damage3 = None
                if "att_3_damage" in tile_properties:
                    damage3 = int(tile_properties["att_3_damage"])
                if "att_3_stun" in tile_properties:
                    stun3 = int(tile_properties["att_3_stun"])
                if "att_3_cooldown" in tile_properties:
                    cooldown3 = int(tile_properties["att_3_cooldown"])
                if "att_3_projectile_amount" in tile_properties:
                    proj3 = int(tile_properties["att_3_projectile_amount"])
                if "att_3_projectile_lifetime" in tile_properties:
                    proj_life3 = int(tile_properties["att_3_projectile_lifetime"])
                if "att_3_spread_angle" in tile_properties:
                    spread3 = int(tile_properties["att_3_spread_angle"])
                if "att_3_projectile_speed" in tile_properties:
                    proj_speed3 = int(tile_properties["att_3_projectile_speed"])
                if "att_3_pierce" in tile_properties:
                    att3_pierce = tile_properties["att_3_pierce"] == "1"
                #Create projectile image
                effect_ID = None
                if ai_ID == "pink_boss":
                    proj_image = "pink_proj.png"
                    proj_anim_list = [2, 2]
                    proj_anim_time_list = [50, 13]
                    proj_width = 32
                    proj_height = 32
                    effect_ID = self.create_attack_effect('tentakel2.png',
                                                      200, 200, 8, 52)
                if damage3: #Attack exists
                    particle_emitter3 = self.create_attack(position, damage3, stun3,
                                                          cooldown3, proj3, proj_image,
                                                          proj_anim_list, proj_anim_time_list,
                                                          proj_width, proj_height,
                                                          proj_life3, proj_speed3, [0,0],
                                                          spread3, effect_ID)
                    particle_emitter3.piercing = att3_pierce
                    attack_list.append(particle_emitter3)
                
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
                    damage1 = int(tile_properties["att_1_damage"])
                if "att_1_stun" in tile_properties:
                    stun1 = int(tile_properties["att_1_stun"])
                if "att_1_cooldown" in tile_properties:
                    cooldown1 = int(tile_properties["att_1_cooldown"])
                if "att_1_projectile_amount" in tile_properties:
                    proj1 = int(tile_properties["att_1_projectile_amount"])
                if "att_1_projectile_lifetime" in tile_properties:
                    proj_life1 = int(tile_properties["att_1_projectile_lifetime"])
                if "att_1_spread_angle" in tile_properties:
                    spread1 = int(tile_properties["att_1_spread_angle"])
                if "att_1_projectile_speed" in tile_properties:
                    proj_speed1 = int(tile_properties["att_1_projectile_speed"])
                if "att_1_pierce" in tile_properties:
                    att1_pierce = tile_properties["att_1_pierce"] == "1"
                #Create players attacks
                attack_list = list()
                #Attack 1:
                effect_ID = self.create_attack_effect('char_attack1_effect.png',
                                                      250, 250, 8, 30)
                #Create projectile image
                proj_image = "simple_projectile_light_circle.png"
                proj_anim_list = [2, 4]
                proj_anim_time_list = [20, 13]
                particle_emitter = self.create_attack(position, damage1, stun1,
                                                      cooldown1, proj1, proj_image,
                                                      proj_anim_list, proj_anim_time_list,
                                                      25, 25,
                                                      proj_life1, proj_speed1, [0,0],
                                                      spread1, effect_ID)
                particle_emitter.piercing = att1_pierce
                attack_list.append(particle_emitter)
                self.create_player(position, hp, max_x_vel, max_y_vel,
                                   attack_list)

            elif tile_properties["type"] == "heal_potion":
                #Add fields
                recovery = int(tile_properties["recovery"])
                size = tile_properties["size"]
                tags = list()
                tags.append("heal_potion")
                collider = components.Collider(x*64, y*64, 64, 64, tags)
                image_name = 'heal_potion_s.png'
                if size == 'l':
                    image_name = 'heal_potion_l.png'
                elif size == 'm':
                    image_name = 'heal_potion_m.png'
                temp = pygame.image.load(os.path.join('data', image_name))
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

    def create_attack(self, position, damage, stun, cooldown, proj_amount,
                      projectile_image, proj_anim_list, proj_anim_time_list,
                      width, height, projlife, projspeed, accel, spread, effect_ID=None):
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
        :param projspeed: projectile_speed
        :type projspeed: int
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
                                   proj_amount, projectile_image, proj_anim_list,
                                   proj_anim_time_list, width, height, projlife,
                                   projspeed, [0, 0], spread, effect_ID)
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
        if ai_ID == "green_1":
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
            
            enemy_AI = ai.AI_1(self, enemy_ID, self.event_manager)
            self.add_component_to_entity(enemy_ID, enemy_AI)
            self.add_component_to_entity(enemy_ID, attack_list)

        elif ai_ID == "pink_1":
            #Enemy's hitbox, it is 50 pixel width and 96 pixel height
            coll = components.Collider(position[0], position[1], 50, 96)
            vel = components.Velocity(0, 0, max_x_vel, max_y_vel)
            #Create enemy's animations
            temp = pygame.image.load(os.path.join('data', 'enemy_pink_1.png')).convert_alpha()
            anim_list = [4, 8, 6, 8, 2, 4]
            anim_time_list = [240, 60, 44, 58, 10, 44]
            anim = components.Appearance(temp, 243, 128, anim_list, anim_time_list)
            anim.rect.center = coll.center
            direction = components.Direction([1, 0])
            hp = components.Health(max_hp)
            c = (coll, direction, vel, anim, hp)
            enemy_ID = self.create_entity(c)
            
            enemy_AI = ai.AI_2(self, enemy_ID, self.event_manager)
            self.add_component_to_entity(enemy_ID, enemy_AI)
            self.add_component_to_entity(enemy_ID, attack_list)
        elif ai_ID == "pink_boss":
            #Enemy's hitbox, it is 50 pixel width and 96 pixel height
            coll = components.Collider(position[0], position[1], 86, 170)
            vel = components.Velocity(0, 0, max_x_vel, max_y_vel)
            #Create enemy's animations
            temp = pygame.image.load(os.path.join('data', 'enemy_pink_boss.png')).convert_alpha()
            anim_list = [4, 2, 5, 8, 2, 4, 5, 5]
            anim_time_list = [240, 60, 44, 58, 10, 44, 44, 44]
            anim = components.Appearance(temp, 250, 200, anim_list, anim_time_list)
            anim.rect.center = coll.center
            direction = components.Direction([1, 0])
            hp = components.Health(max_hp)
            c = (coll, direction, vel, anim, hp)
            enemy_ID = self.create_entity(c)
            
            enemy_AI = ai.AI_Boss_2(self, enemy_ID, self.event_manager)
            self.add_component_to_entity(enemy_ID, enemy_AI)
            self.add_component_to_entity(enemy_ID, attack_list)
        self.deactivate_entity(enemy_ID)

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
                        self.create_game_object(x, y, tile_properties)
        self.create_curse()
        