"""
.. module:: rendersystem
   :Platform: Unix, Windows
   :Synopsis: Render system to display all game objects.
"""

import pygame
import events
import pyscroll
import parallaxStarfield

class RenderSystem(object):
    """Render system displays a parallax starfield, the tmx-Level and all game objects, which are stored in world.appearance.
    
    :Attributes:
        - *evManager* (events.EventManager): event manager
        - *world* (gameworld.GameWorld): game world with game objects and level
        - *screen* (pygame.Surface): game screen, where all the stuff is drawn
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
        self.screen = world.screen
        w, h = world.screen.get_size()
        #Create new renderer/camera
        self.map_layer = pyscroll.BufferedRenderer(self.world.level.map_data,
                                                   (w, h),
                                                   clamp_camera=False,
                                                   colorkey=None,
                                                   alpha=True)
        #The player, enemies, items etc. should to be on top of
        #layer named in TMX "decoration behind"
        #Find layer number of the layer named "decoration behind"
        self.render_layer = 0
        for layer_index in range(len(self.world.level.tmx_data.layers)):
            if self.world.level.tmx_data.layers[layer_index].name == "decoration behind":
                self.render_layer = layer_index
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer,
                                            default_layer=self.render_layer)
        #Players image position is actually camera position
        player_image_position = self.world.appearance[self.world.player].rect
        #Parallax background
        self.star_field = parallaxStarfield.ParallaxStarfield(self.screen,
                                                              player_image_position.x,
                                                              player_image_position.y)

    def notify(self, event):
        """ Notify, when an event occurs. 
        
        :param event: occurred event
        :type event: events.Event
        """
        if not self.world.game_paused:
            if isinstance(event, events.TickEvent):
                self.draw(event.dt)
            if isinstance(event, events.ResizeWindowEvent):
                self.resize(event.width, event.height)

    def update(self):
        """ Updates group, so new entities can be added and dead removed.
        
        Every update the default layer, where all game entities
        are drawn, should be cleaned and reassigned.
        """
        self.group.remove_sprites_of_layer(self.render_layer)
        # Add all game components
        for image in self.world.appearance.itervalues():
            if image.play_animation:
                self.group.add(image)

    def draw(self, dt):
        """ Draw everything on the screen.
        
        :param dt: CPU tick
        :type dt: int
        """
        # First update and draw the starfield
        # to update the starfield we need the players position
        # because camera is centered on player
        player_image_position = self.world.appearance[self.world.player].rect
        self.star_field.move(player_image_position.x, player_image_position.y)
        self.star_field.draw()
        # Update game objects
        self.update()
        self.group.update(dt)
        # Center the map/screen on the player
        self.group.center(self.world.collider[self.world.player].center)
        # Draw the level and all other sprites
        self.group.draw(self.screen)
        pygame.display.flip()

    def resize(self, w, h):
        """ Resize game window.
        
        :param w: new width in pixels
        :type w: int
        :param h: new height in pixels
        :type h: int
        """
        pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.map_layer.set_size((w, h))
