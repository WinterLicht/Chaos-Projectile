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
        if hasattr(event, 'entity_ID'):
            entity_ID = event.entity_ID
            if isinstance(event, events.UpdateImagePosition):
                self.update_image_position(entity_ID, event.new_position)
            if not self.world.appearance[entity_ID].play_animation_till_end:
                if isinstance(event, events.EntityAttacks):
                    self.play_attack_animation(entity_ID)
                if isinstance(event, events.EntityJump):
                    if not self.jump_animation_running(entity_ID):
                        self.play_jump_animation(entity_ID)
                if isinstance(event, events.EntityMovesLeft):
                    self.world.appearance[entity_ID].flip = True
                    if not self.walk_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                        self.play_walk_animation(entity_ID)
                if isinstance(event, events.EntityMovesRight):
                    self.world.appearance[entity_ID].flip = False
                    if not self.walk_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                        self.play_walk_animation(entity_ID)
                if isinstance(event, events.EntityStopMovingLeft):
                    if not self.idle_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                        self.play_idle_animation(entity_ID)
                if isinstance(event, events.EntityStopMovingRight):
                    if not self.idle_animation_running(entity_ID) and not self.jump_animation_running(entity_ID):
                        self.play_idle_animation(entity_ID)
                if isinstance(event, events.EntityGrounded):
                    if self.jump_animation_running(entity_ID):
                        self.play_idle_animation(event.entity_ID)
                if isinstance(event, events.EntityDies):
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
                                #Death animation ended
                                if self.death_animation_running(entity_ID):
                                    ev_remove_ent = events.RemoveEntityFromTheGame(entity_ID)
                                    self.event_manager.post(ev_remove_ent)
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

    def idle_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 0

    def play_idle_animation(self, entity_ID):
        #Idle animation is 0
        self.world.appearance[entity_ID].current_animation = 0
        self.world.appearance[entity_ID].current_frame_x = 0
        
    def walk_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 1
    
    def play_walk_animation(self, entity_ID):
        #Walk animation is 1
        self.world.appearance[entity_ID].current_animation = 1
        self.world.appearance[entity_ID].current_frame_x = 0
    
    def jump_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 2
    
    def play_jump_animation(self, entity_ID):
        #Jump animation is 2
        self.world.appearance[entity_ID].current_animation = 2
        self.world.appearance[entity_ID].current_frame_x = 0
    
    def play_attack_animation(self, entity_ID):
        #Attack animation is 2
        self.world.appearance[entity_ID].play_animation_till_end = True
        self.world.appearance[entity_ID].current_animation = 2
        self.world.appearance[entity_ID].current_frame_x = 0
        
    def death_animation_running(self, entity_ID):
        current_animation = self.world.appearance[entity_ID].current_animation
        return current_animation == 1
    
    def play_death_animation(self, entity_ID):
        #Death animation is 3
        self.world.appearance[entity_ID].play_animation_till_end = True
        self.world.appearance[entity_ID].play_once = True
        self.world.appearance[entity_ID].current_animation = 1
        self.world.appearance[entity_ID].current_frame_x = 0

