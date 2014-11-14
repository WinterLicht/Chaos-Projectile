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
        if isinstance(event, events.PlayerMoved):
            self.handle_player_moved_event()
        if isinstance(event, events.PlayerStoppedMovement):
            self.handle_player_stopped_movement_event()
        if isinstance(event, events.UpdateImagePosition):
            self.update_image_position(event.entity_ID,
                                       event.new_position)

    def run_animations(self, dt):
        """Computes which animation frame should be displayed.
        Every CPU tick checks if new frame should be displayed. Therefore there is a counter for each animation that measures time. When time equal delay between frames passed, next frame will be displayed.
        
        :param dt: time passed
        :type dt: int
        """
        for animation in self.world.appearance.itervalues():
            #For every animation
            if animation.frames[animation.current_animation] > 1:
                if animation.counter % animation.delay_between_frames[animation.current_animation] == 0:
                    #Time equal delay between frames passed, so next frame
                    if animation.current_frame_x < animation.frames[animation.current_animation]-1:
                        animation.current_frame_x = animation.current_frame_x + 1
                    else:
                        #Animation ended, begin from 0
                        animation.current_frame_x = 0
                animation.counter = animation.counter + 1
                animation.set_image(animation.current_frame_x)
            else:
                animation.set_image(animation.current_frame_x)

    def handle_player_stopped_movement_event(self):
        """When player doesn't move or attack, then show his idle animation."""
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

    def handle_player_moved_event(self):
        """When player moves and doesn't attack, show walk or jump animation."""
        player = self.world.player
        current_animation = self.world.appearance[player].current_animation
        if not self.world.velocity[player][0] == 0:
            #Flip sprite:
            self.world.appearance[player].flip = self.world.velocity[player][0] < 0
        if self.world.state[player].grounded and not current_animation == 1:
            #Walk animation is 1
            #Reset to this when player moves, is grounded
            self.world.appearance[player].current_animation = 1
            self.world.appearance[player].current_frame_x = 0
        if not self.world.state[player].grounded and not current_animation == 2:
            #Jump animation is 2
            #Reset to this when player isn't grounded
            self.world.appearance[player].current_animation = 2
            self.world.appearance[player].current_frame_x = 0

    def update_image_position(self, entity_ID, new_position):
        """Update image position, when corresponding entity moved.
        
        :param entity_ID: entity
        :type entity_ID: int
        :param new_position: new position of the entity
        :type new_position: int tuple
        """
        if entity_ID in self.world.appearance:
            self.world.appearance[entity_ID].rect.center = new_position
