"""
.. module:: inputSystem
    :platform: Unix, Windows
    :synopsis: Translates events from controllers to actions.
"""

import pygame
import events


class InputSystem(object):
    """Gets events from controllers and translates this to actions

    :Attributes:
        - *world* (gameWorld.GameWorld): game world
        - *event_manager* (events.EventManager): event manager
    """

    def __init__(self, event_manager, world):
        """
        :param event_manager: event manager
        :type event_manager: events.EventManager
        :param world: game world
        :type world: gameWorld.GameWorld
        """
        self.world = world
        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        
        # Keys UP, DOWN, LEFT, RIGHT control aim and attacks direction. This is for custom controller with makey makey board.
        # To store state of arrow keys
        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False

    def notify(self, event):
        """Notify, when event occurs. 

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TickEvent):
            self.handle_arrow_keys()
        if isinstance(event, events.KeyPressed):
            self.handle_key_pressed(event.key)
        if isinstance(event, events.KeyReleased):
            self.handle_key_released(event.key)
        if isinstance(event, events.MouseMoved):
            self.handle_mouse_move(event.x, event.y)
        if isinstance(event, events.HatMoved):
            self.handle_hat_moved(event.x, event.y)
        if isinstance(event, events.AxisMoved):
            self.handle_joystick(event.x_axis, event.y_axis)
        if isinstance(event, events.MouseButtonDown):
            self.handle_attack_request()

    def handle_hat_moved(self, x, y):
        """Hat controlls player movement.

        :param x: x position
        :type x: int
        :param y: y position
        :type y: int
        """
        if x < 0:
            #Walk left
            ev = events.EntityMovesLeftRequest(self.world.player)
            self.event_manager.post(ev)
        elif x > 0:
            #Walk right
            ev = events.EntityMovesRightRequest(self.world.player)
            self.event_manager.post(ev)
        else:
            ev = events.EntityStopMovingLeftRequest(self.world.player)
            self.event_manager.post(ev)
            ev = events.EntityStopMovingRightRequest(self.world.player)
            self.event_manager.post(ev)
        if y > 0:# and self.world.state[self.world.player].grounded:
            #Jump
            ev = events.EntityJumpRequest(self.world.player)
            self.event_manager.post(ev)
        #else:
            #ev = events.EntityStopJumpRequest(self.world.player)
            #self.event_manager.post(ev)

    def handle_joystick(self, x_axis, y_axis):
        """Joystick controls aim and attacks direction.

        :param x_axis: x position of the axis
        :type x_axis: float
        :param y_axis: y position of the axis
        :type y_axis: float
        """
        #Take into account some tolerance to handle jitter
        epsilon = 0.5
        if x_axis > epsilon:
            x_axis = 1
        elif x_axis < -epsilon:
            x_axis = -1
        else:
            x_axis = 0
        if y_axis > epsilon:
            y_axis = 1
        elif y_axis < -epsilon:
            y_axis = -1
        else:
            y_axis = 0
        #Determine rotation for the orb according in which octant axis is
        self.move_orb(x_axis, y_axis)

    def handle_arrow_keys(self):
        """Helper Function for aiming with arrow keys"""
        x_axis = 0
        y_axis = 0
        '''
        if self.key_up and not self.key_down and not self.key_right and not self.key_left:
            #aim up
            y_axis = -1
        elif not self.key_up and self.key_down and not self.key_right and not self.key_left:
            #aim down
            y_axis = 1
        elif not self.key_up and not self.key_down and not self.key_right and self.key_left:
            #aim left
            x_axis = -1
        elif not self.key_up and not self.key_down and self.key_right and not self.key_left:
            #aim right
            x_axis = 1
        elif not self.key_up and not self.key_down and self.key_right and not self.key_left:
            #aim right
            x_axis = 1
        '''
        if self.key_down:
            y_axis = 1
        if self.key_up:
            y_axis = -1
        if self.key_left:
            x_axis = -1
        if self.key_right:
            x_axis = 1
        #Determine rotation for the orb according which keys are pressed   
        self.move_orb(x_axis, y_axis)
        if not (x_axis == 0 and y_axis == 0):
           self.handle_attack_request()

    def handle_key_pressed(self, key):
        """Keys A, D and W controll players movement.

        :param key: key pressed
        :type key: pygame constant
        """
        if key == pygame.K_a:
            #Walk left
            ev = events.EntityMovesLeftRequest(self.world.player)
            self.event_manager.post(ev)
        if key == pygame.K_d:
            #Walk right
            ev = events.EntityMovesRightRequest(self.world.player)
            self.event_manager.post(ev)
        if key == pygame.K_w:
            #Jump
            ev = events.EntityJumpRequest(self.world.player)
            self.event_manager.post(ev)

        elif key == pygame.K_UP and not self.key_down:
            self.key_up = True
        elif key == pygame.K_DOWN and not self.key_up:
            self.key_down = True
        elif key == pygame.K_LEFT and not self.key_right:
            self.key_left = True
        elif key == pygame.K_RIGHT and not self.key_left:
            self.key_right = True

    def handle_key_released(self, key):
        """Player stops movement, when key is released.

        :param key: key pressed
        :type key: pygame constant
        """
        if key == pygame.K_a:
            ev = events.EntityStopMovingLeftRequest(self.world.player)
            self.event_manager.post(ev)
        elif key == pygame.K_d:
            ev = events.EntityStopMovingRightRequest(self.world.player)
            self.event_manager.post(ev)
        elif key == pygame.K_UP:
            self.key_up = False
        elif key == pygame.K_DOWN:
            self.key_down = False
        elif key == pygame.K_LEFT:
            self.key_left = False
        elif key == pygame.K_RIGHT:
            self.key_right = False

    def handle_attack_request(self):
        #Execute players attacks number 0
        ev = events.EntityAttackRequest(self.world.player, 0)
        self.event_manager.post(ev)

    def handle_mouse_move(self, mouse_x, mouse_y):
        """Position of the mouse cursor controlls aim and attacks direction.

        :param mouse_x: x mouse position in pixel in screen coordinates
        :type mouse_x: int
        :param mouse_y: y mouse position in pixel in screen coordinates
        :type mouse_x: int
        """
        #Subtract offset, so mouse coordinates are relative to screen middle
        mouse_x = mouse_x - pygame.display.Info().current_w / 2
        mouse_y = mouse_y - pygame.display.Info().current_h / 2

        #Calculate in which octant is mouse cursor
        #Small offset between octants
        epsilon = 30
        if epsilon > mouse_x and mouse_x > -epsilon:
            direction_x = 0
        else:
            if mouse_x > 0:
                direction_x = 1
            else:
                direction_x = -1
        if epsilon > mouse_y and mouse_y > -epsilon:
            direction_y = 0
        else:
            if mouse_y > 0:
                direction_y = 1
            else:
                direction_y = -1
        #Determine rotation for the orb according in which octant cursor is
        self.move_orb(direction_x, direction_y)

    def move_orb(self, x, y):
        """Moves and rotates the orb according players aim input.

        No rotation is when aim direction is right from the player.

        :param x: x position in octant
        :type x: int
        :param y: y position in octant
        :type y: int
        """
        angle = 0
        if x == 1 and y == -1:
            x = 0.75
            y = -0.75
            angle = 45
        elif x == 0 and y == -1:
            angle = 90
        elif x == -1 and y == -1:
            x = -0.75
            y = -0.75
            angle = 135
        elif x == -1 and y == 0:
            angle = 180
        elif x == -1 and y == 1:
            x = -0.75
            y = 0.75
            angle = 225
        elif x == 0 and y == 1:
            angle = 270
        elif x == 1 and y == 1:
            x = 0.75
            y = 0.75
            angle = 315
        if not (x == 0 and y == 0):
            #Axis moved, so update orb position
            player_ID = self.world.player
            orb_ID = self.world.players[self.world.player].orb_ID
            self.world.direction[player_ID] = [x, y]
            #Move orb
            self.world.appearance[orb_ID].rect.center = (x*64 + self.world.collider[self.world.player].center[0] ,
                                                        y*64 + self.world.collider[self.world.player].center[1])
            #Save rotation for orbs sprite
            self.world.appearance[orb_ID].angle = angle
            #Rotate hp-ui
            hp_ID = self.world.players[self.world.player].hp_ID
            self.world.appearance[hp_ID].rect.center = self.world.appearance[orb_ID].rect.center
            #self.world.appearance[hp_ID].angle = angle
            
