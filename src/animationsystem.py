"""
.. module:: animationsystem
    :platform: Unix, Windows
    :synopsis: Computes which frame of animation should be displayed.
"""

import events

class AnimationSystem(object):
    """Computes which frame of animation should be displayed.
    
    :Attributes:
        - *evManager*: event manager 
        - *world*: game world
    """
    
    def __init__(self, event_manager, world):
        """
        :param event_manager: event manager
        :type event_manager: events.EventManager
        :param world: game world
        :type world: gameworld.GameWorld
        """
        self.world = world
        self.event_manager = event_manager
        self.event_manager.register_listener(self)

    def notify(self, event):
        """Notify, when event occurs. 
        
        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            self.run_animations(event.dt)
        if isinstance(event, events.UpdatePlayersHpUI):
            self.update_players_hp_ui(event.player_ID)
        if hasattr(event, 'entity_ID'):
            entity_ID = event.entity_ID
            if isinstance(event, events.UpdateImagePosition):
                self.update_image_position(entity_ID, event.new_position)
            if entity_ID in self.world.appearance:
                if not self.world.appearance[entity_ID].play_animation_till_end and not self.stun_animation_running(entity_ID):
                    if isinstance(event, events.EntityAttacks):
                        self.play_attack_animation(entity_ID, event.attack_Nr)
                    elif isinstance(event, events.EntityJump):
                        if not self.jump_animation_running(entity_ID):
                            self.play_jump_animation(entity_ID)
                    elif isinstance(event, events.EntityMovesLeft):
                        self.world.appearance[entity_ID].flip = True
                        if not self.walk_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                            self.play_walk_animation(entity_ID)
                    elif isinstance(event, events.EntityMovesRight):
                        self.world.appearance[entity_ID].flip = False
                        if not self.walk_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                            self.play_walk_animation(entity_ID)
                    elif isinstance(event, events.EntityStopMovingLeft):
                        if not self.idle_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                            self.play_idle_animation(entity_ID)
                    elif isinstance(event, events.EntityStopMovingRight):
                        if not self.idle_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                            self.play_idle_animation(entity_ID)
                    elif isinstance(event, events.EntityGrounded):
                        if self.jump_animation_running(entity_ID) or "no_gravity" in self.world.collider[entity_ID].tags:
                            if not self.idle_animation_running(entity_ID):
                                self.play_idle_animation(entity_ID)
                if isinstance(event, events.ActivateEntity):
                    self.play_idle_animation(entity_ID)
                '''
                if isinstance(event, events.PlayIdleAnimation):
                    self.world.appearance[entity_ID].current_animation = 0
                    if self.world.appearance[entity_ID].frames[0] < self.world.appearance[entity_ID].current_frame_x:
                        self.world.appearance[entity_ID].current_frame_x = 0
                '''
                if isinstance(event, events.EntityStunned):
                    self.play_stun_animation(entity_ID, event.duration)
                if isinstance(event, events.EntityDies):
                    if not self.death_animation_running(entity_ID):
                        self.play_death_animation(entity_ID)

    def run_animations(self, dt):
        """Computes which animation frame should be displayed.
        Every CPU tick checks if new frame should be displayed. Therefore there is a counter for each animation that measures time. When time equal delay between frames passed, next frame will be displayed.
        
        :param dt: time passed
        :type dt: int
        """
        for entity_ID, animation in self.world.appearance.iteritems():
            if animation.play_animation:
                #For every animation
                animation.set_image(animation.current_frame_x)
                if animation.frames[animation.current_animation] > 1:
                    if animation.counter % animation.delay_between_frames[animation.current_animation] == 0:
                        #Time equal delay between frames passed, so next frame
                        if animation.current_frame_x < animation.frames[animation.current_animation]-1:
                            animation.current_frame_x = animation.current_frame_x + 1
                        else:
                            if animation.play_animation_till_end:
                                #Animation played already till end
                                animation.play_animation_till_end = False
                            if animation.play_once:
                                #Animation played once
                                animation.play_animation = False
                                #Self destructing image?
                                if animation.self_destruct:
                                    ev_remove_ent = events.RemoveEntityFromTheGame(entity_ID)
                                    self.event_manager.post(ev_remove_ent)
                                #Death animation ended
                                if self.death_animation_running(entity_ID):
                                    ev_remove_ent = events.RemoveEntityFromTheGame(entity_ID)
                                    self.event_manager.post(ev_remove_ent)
                                #Stun animation ended
                                if self.stun_animation_running(entity_ID):
                                    ev_activate = events.ActivateEntity(entity_ID)
                                    self.event_manager.post(ev_activate)
                            #Loop Animation
                            #Animation ended, begin from 0
                            animation.current_frame_x = 0
                    animation.counter = animation.counter + 1
                    #animation.set_image(animation.current_frame_x)
                #else:
                    #animation.set_image(animation.current_frame_x)

    def update_image_position(self, entity_ID, new_position):
        """Update image position, when corresponding entity moved.
        
        :param entity_ID: entity
        :type entity_ID: int
        :param new_position: new position of the entity
        :type new_position: int tuple
        """
        if entity_ID in self.world.appearance:
            self.world.appearance[entity_ID].rect.center = new_position
        #When moving object was a player
        if self.world.player == entity_ID:
            #Update orb direction correspondent aim direction and
            #player position
            orb_ID = self.world.players[entity_ID].orb_ID
            directionX = self.world.direction[entity_ID][0]
            directionY = self.world.direction[entity_ID][1]
            self.world.appearance[orb_ID].rect.center = (directionX*64 + self.world.collider[self.world.player].center[0],
                                                         directionY*64 + self.world.collider[self.world.player].center[1])
            #Update hp gui
            hp_ID = self.world.players[entity_ID].hp_ID
            self.world.appearance[hp_ID].rect.center = self.world.appearance[orb_ID].rect.center

    def update_players_hp_ui(self, player_ID):
        players_health = self.world.hp[self.world.players[player_ID].hp_ID]
        hp_image_index = players_health.points // (players_health.max // (len(players_health.hp_sprites) - 1))
        if(hp_image_index < 0):
            hp_image_index = 0
        players_health.current_image = players_health.hp_sprites[hp_image_index]
        self.world.appearance[self.world.players[player_ID].hp_ID] = players_health.current_image

    def idle_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 0

    def play_idle_animation(self, entity_ID):
        #Idle animation is 0
        self.world.appearance[entity_ID].current_animation = 0
        self.world.appearance[entity_ID].current_frame_x = 0
        self.world.appearance[entity_ID].play_animation_till_end = False
        self.world.appearance[entity_ID].play_once = False
        self.world.appearance[entity_ID].play_animation = True
        
    def walk_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 3
    
    def play_walk_animation(self, entity_ID):
        #Walk animation is 3
        if len(self.world.appearance[entity_ID].frames) > 3:
            self.world.appearance[entity_ID].current_animation = 3
            self.world.appearance[entity_ID].current_frame_x = 0
            self.world.appearance[entity_ID].play_animation_till_end = False
            self.world.appearance[entity_ID].play_once = False
            self.world.appearance[entity_ID].play_animation = True
    
    def jump_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 5
    
    def play_jump_animation(self, entity_ID):
        #Jump animation is 5
        if len(self.world.appearance[entity_ID].frames) > 2:
            self.world.appearance[entity_ID].current_animation = 5
            self.world.appearance[entity_ID].current_frame_x = 0
            self.world.appearance[entity_ID].play_animation_till_end = False
            self.world.appearance[entity_ID].play_once = False
            self.world.appearance[entity_ID].play_animation = True
    
    def play_attack_animation(self, entity_ID, attack_Nr):
        #First Attack animation is 2
        if len(self.world.appearance[entity_ID].frames) > 2 and attack_Nr == 0:
            self.world.appearance[entity_ID].play_animation = True
            self.world.appearance[entity_ID].play_animation_till_end = False
            self.world.appearance[entity_ID].play_animation_till_end = True
            self.world.appearance[entity_ID].current_animation = 2
            self.world.appearance[entity_ID].current_frame_x = 0
        #For other attack animations
        elif len(self.world.appearance[entity_ID].frames) > (5+attack_Nr) and attack_Nr > 0:
            self.world.appearance[entity_ID].play_animation = True
            self.world.appearance[entity_ID].play_animation_till_end = False
            self.world.appearance[entity_ID].play_animation_till_end = True
            self.world.appearance[entity_ID].current_animation = 5+attack_Nr
            self.world.appearance[entity_ID].current_frame_x = 0
        
    def death_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 1
    
    def play_death_animation(self, entity_ID):
        #Death animation is 1
        if len(self.world.appearance[entity_ID].frames) > 1:
            self.world.appearance[entity_ID].play_animation_till_end = True
            self.world.appearance[entity_ID].play_once = True
            self.world.appearance[entity_ID].current_animation = 1
            self.world.appearance[entity_ID].current_frame_x = 0
            self.world.appearance[entity_ID].play_animation = True

    def stun_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 4
    
    def play_stun_animation(self, entity_ID, duration):
        #Stun animation is 4
        if len(self.world.appearance[entity_ID].frames) > 0:
            self.world.appearance[entity_ID].current_animation = 4
            self.world.appearance[entity_ID].set_animation_duration(4, duration)
            self.world.appearance[entity_ID].current_frame_x = 0
            self.world.appearance[entity_ID].play_once = True
            self.world.appearance[entity_ID].play_animation_till_end = True
            self.world.appearance[entity_ID].play_animation = True
