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
        if isinstance(event, events.UpdateImagePosition):
            self.update_image_position(event.entity_ID,
                                       event.new_position)
        #if isinstance(event, events.PlayerStoppedMovement):
        #    self.handle_player_stopped_movement_event()
        #if isinstance(event, events.PlayerMoved):
        #    self.handle_player_moved_event()

    def run_animations(self, dt):
        """Computes which animation frame should be displayed.
        Every CPU tick checks if new frame should be displayed. Therefore there is a counter for each animation that measures time. When time equal delay between frames passed, next frame will be displayed.
        
        :param dt: time passed
        :type dt: int
        """
        for entity_ID in self.world.state:
            self.determine_animation(entity_ID)
        for animation in self.world.appearance.itervalues():
            if animation.play_animation:
                #For every animation
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
                            #Loop Animation
                            #Animation ended, begin from 0
                            animation.current_frame_x = 0
                    animation.counter = animation.counter + 1
                    animation.set_image(animation.current_frame_x)
                else:
                    animation.set_image(animation.current_frame_x)

    def determine_animation(self, entity_ID):
        """Determines which animation should be played depending on the state of an entity.
        
        :param entity_ID: For this entity an animation will be determined 
        :type entity_ID: int
        """
        current_animation = self.world.appearance[entity_ID].current_animation
        state = self.world.state[entity_ID]
        if self.world.velocity[entity_ID]:
            if not self.world.velocity[entity_ID][0] == 0:
                self.world.appearance[entity_ID].flip = self.world.velocity[entity_ID][0] < 0
        if not self.world.appearance[entity_ID].play_animation_till_end:
            if state.attacks > -1:
                #Attack animation is 2
                self.world.appearance[entity_ID].play_animation_till_end = True
                self.world.appearance[entity_ID].current_animation = 2
                self.world.appearance[entity_ID].current_frame_x = 0
            elif (state.walk_left or state.walk_right) and state.grounded and not current_animation == 1:
                #Walk animation is 1
                #Reset to this when player moves, is grounded
                self.world.appearance[entity_ID].current_animation = 1
                self.world.appearance[entity_ID].current_frame_x = 0
            elif (state.jumping or not state.grounded) and not current_animation == 2:
                #Jump animation is 2
                #Reset to this when player isn't grounded
                self.world.appearance[entity_ID].current_animation = 2
                self.world.appearance[entity_ID].current_frame_x = 0
            elif not state.walk_left and not state.walk_right and \
            self.world.state[entity_ID].grounded and \
            not current_animation == 0:
                #Idle animation is 0
                #Reset to idle, if it's not already played
                self.world.appearance[entity_ID].current_animation = 0
                self.world.appearance[entity_ID].current_frame_x = 0

    def update_image_position(self, entity_ID, new_position):
        """Update image position, when corresponding entity moved.
        
        :param entity_ID: entity
        :type entity_ID: int
        :param new_position: new position of the entity
        :type new_position: int tuple
        """
        if entity_ID in self.world.appearance:
            self.world.appearance[entity_ID].rect.center = new_position
        if entity_ID == self.world.player:
            player = self.world.players[entity_ID]
            player_state = self.world.state[entity_ID]
            attack_Nr = player_state.attacks
            effect_ID = self.world.attacks[entity_ID][attack_Nr].effect_ID
            #Get the orb position of the player
            orb_position = self.world.appearance[player.orb_ID].rect.center
            #Update position and rotation of the attack effect
            self.world.appearance[effect_ID].rect.center = orb_position
            self.world.appearance[effect_ID].angle = self.world.appearance[player.orb_ID].angle 

    def handle_player_moved_event(self):
        player = self.world.player
        current_animation = self.world.appearance[player].current_animation
        state = self.world.state[player]
        if state.grounded and not current_animation == 1:
            #Walk animation is 1
            #Reset to this when player moves, is grounded
            self.world.appearance[player].current_animation = 1
            self.world.appearance[player].current_frame_x = 0

    def handle_player_stopped_movement_event(self):
        """When player doesn't move or attack, then show his idle animation.
        """

        player = self.world.player
        if not self.world.velocity[player][0] == 0:
            #Flip sprite:
            self.world.appearance[player].flip = self.world.velocity[player][0] < 0
        current_animation = self.world.appearance[player].current_animation
        if self.world.state[player].grounded and not current_animation == 0:
                #Idle animation is 0
                #Reset to idle, if it's not already played
                self.world.appearance[player].current_animation = 0
                self.world.appearance[player].current_frame_x = 0
