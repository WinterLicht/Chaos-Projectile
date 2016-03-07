"""
.. module:: soundsystem
   :Platform: Unix, Windows
   :Synopsis: Sound system
"""

import os
import pygame

import events
import ai

class SoundSystem(object):
    """Render system.
    
    :Attributes:
        - *evManager*: event manager
        - *world*: game world
        - *screen*: game screen
    """

    def __init__(self, event_manager, world):
        """
        :param event_manager: event Manager
        :type event_manager: events.EventManager
        :param world: game world
        :type world: gameWorld.GameWorld
        """
        self.world = world
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        #Load all sounds
        filename = self.get_sound_file('BG_loop1.ogg')
        self.bg_no_enemy = pygame.mixer.Sound(filename)
        self.bg_no_enemy.play(-1)
        filename = self.get_sound_file('BG_loop2.ogg')
        self.bg_enemy_near = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('BG_loop3.ogg')
        self.bg_boss = pygame.mixer.Sound(filename)
        self.bg_enemy_near_running = False
        self.bg_boss_running = False
        #Player Sounds
        filename = self.get_sound_file('Shot1.ogg')
        self.shot_1_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Shot2.ogg')
        self.shot_2_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Shot 3.ogg')
        self.shot_3_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Hit Female 1.ogg')
        self.hit_female_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Jump.ogg')
        self.jump_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Landing.ogg')
        self.landing_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Aim Short.ogg')
        self.aim_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Footsteps_loop.ogg')
        self.footsteps_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Collect Item.ogg')
        self.collect_item_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Portal.ogg')
        self.portal_enter_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Appear and Fly 1.ogg')
        self.fly_appear_1_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Appear and Fly 2.ogg')
        self.fly_appear_2_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Appear and Fly 3.ogg')
        self.fly_appear_3_sound = pygame.mixer.Sound(filename)
        filename = self.get_sound_file('Disappear.ogg')
        self.fly_disappear_sound = pygame.mixer.Sound(filename)
        #Helper
        self.helper_player_jump = True
        self.helper_player_walk = False
        self.player_footsteps_playing = False
        #Green Curse sounds
        filename = self.get_sound_file('Die.ogg')
        self.player_dies_sound = pygame.mixer.Sound(filename)

    def notify(self, event):
        """Notify, when event occurs and stop CPUSpinner when it's quit event. 
        
        :param event: occurred event
        :type event: events.Event
        """
        fade_out_time = 1200
        if isinstance(event, events.TickEvent):
            pass
        elif isinstance(event, events.EnemyNear):
            if isinstance(self.world.ai[event.entity_ID], ai.AI_Boss_2):
                if not self.bg_boss_running:
                    self.bg_no_enemy.fadeout(fade_out_time)
                    self.bg_boss.play(-1)
                    self.bg_boss_running = True
                    if self.bg_enemy_near_running:
                        self.bg_enemy_near.fadeout(fade_out_time)
                        self.bg_enemy_near_running = False
            else:
                if not self.bg_enemy_near_running:
                    self.bg_no_enemy.fadeout(fade_out_time)
                    self.bg_enemy_near.play(-1)
                    self.bg_enemy_near_running = True
                    if self.bg_boss_running:
                        self.bg_boss.fadeout(fade_out_time)
                        self.bg_boss_running = False
        elif isinstance(event, events.NoEnemysNear):
            if self.bg_enemy_near_running:
                self.bg_enemy_near.fadeout(fade_out_time)
                self.bg_no_enemy.play(-1)
                self.bg_enemy_near_running = False
            if self.bg_boss_running:
                self.bg_boss.fadeout(fade_out_time)
                self.bg_no_enemy.play(-1)
                self.bg_boss_running = False    
        elif isinstance(event, events.EntityAttacks):
            entity_ID = event.entity_ID
            if entity_ID == self.world.player:
                self.footsteps_sound.stop()
                random_nr = ai.random_(3)
                if random_nr == 0:
                    self.shot_1_sound.play()
                elif random_nr == 1:
                    self.shot_2_sound.play()
                else:
                    self.shot_3_sound.play()
            elif entity_ID in self.world.ai:
                ai_ = self.world.ai[entity_ID]
                if isinstance(ai_, ai.Level1_curse):
                    random_nr = ai.random_(3)
                    if random_nr == 0:
                        self.fly_appear_1_sound.play()
                    elif random_nr == 1:
                        self.fly_appear_2_sound.play()
                    else:
                        self.fly_appear_3_sound.play()
        elif isinstance(event, events.EntityStunned):
            entity_ID = event.entity_ID
            if entity_ID == self.world.player:
                self.footsteps_sound.stop()
                self.hit_female_sound.play()
        elif isinstance(event, events.EntityJump):
            entity_ID = event.entity_ID
            if entity_ID == self.world.player and self.helper_player_jump:
                self.footsteps_sound.stop()
                self.player_footsteps_playing = False
                self.jump_sound.play()
                self.helper_player_jump = False
        elif isinstance(event, events.EntityGrounded):
            entity_ID = event.entity_ID
            if entity_ID == self.world.player and not self.helper_player_jump:
                self.landing_sound.play()
                self.helper_player_jump = True
        elif isinstance(event, events.PlayerAims):
            self.aim_sound.play()
        elif isinstance(event, events.EntityMovesRight) or isinstance(event, events.EntityMovesLeft): 
            player_vel_x = self.world.velocity[self.world.player].x
            if player_vel_x == 0:
                self.footsteps_sound.stop()
                self.player_footsteps_playing = False
            else:
                if not self.player_footsteps_playing and self.helper_player_jump:
                    self.footsteps_sound.play(-1)
                    self.player_footsteps_playing = True
        elif isinstance(event, events.EntityStopMovingRight) or isinstance(event, events.EntityStopMovingLeft):
            entity_ID = event.entity_ID
            if entity_ID == self.world.player:
                self.footsteps_sound.stop()
                self.player_footsteps_playing = False
        elif isinstance(event, events.PortalEntered):
            self.portal_enter_sound.play()
        elif isinstance(event, events.CollectedItem):
            self.collect_item_sound.play()
        elif isinstance(event, events.EntityDies):
            entity_ID = event.entity_ID
            if entity_ID == self.world.player:
                self.player_dies_sound.play()
        
    def get_sound_file(self, filename):
        """Simple helper function to merge the file name and the directory name.
        
        :param filename: file name of TMX file
        :type filename: string
        """
        return os.path.join('data', os.path.join('sounds', filename) )