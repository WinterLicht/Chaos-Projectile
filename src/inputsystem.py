"""
.. module:: inputSystem
    :platform: Unix, Windows
    :synopsis: Translates events from controllers to actions.
"""

import pygame
import events
from controller import Actions
from controller import input_is_a_joystickbutton
from controller import is_aim_action
from controller import is_movement_action


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

        self.continuous_attack = False

    def notify(self, event):
        """Notify, when event occurs. 

        :param event: occured event
        :type event: events.Event
        """
        if isinstance(event, events.TogglePauseEvent):
            if self.world.game_paused:
                self.unpause_game()
            else:
                self.world.game_paused = True
        if isinstance(event, events.ToggleContinuousAttack):
            self.continuous_attack = (not self.continuous_attack)
        if not self.world.game_paused:
            if isinstance(event, events.MouseMoved):
                self.handle_mouse_move(event.x, event.y)
            elif isinstance(event, events.MouseButtonDown):
                self.handle_attack_request()
            elif isinstance(event, events.SentInputAction):
                self.handle_input(event)
            elif self.continuous_attack:
                if isinstance(event, events.TickEvent):
                   self.handle_arrow_keys()

    def handle_input(self, event):
        #Movement
        if (event.action == Actions.MOVE_LEFT and event.input.type == pygame.KEYDOWN):
            ev = events.EntityMovesLeftRequest(self.world.player)
            self.event_manager.post(ev)
        elif (event.input.type == pygame.KEYDOWN and event.action == Actions.MOVE_RIGHT):
            ev = events.EntityMovesRightRequest(self.world.player)
            self.event_manager.post(ev)
        elif (event.action == Actions.MOVE_LEFT and event.input.type == pygame.KEYUP):
            ev = events.EntityStopMovingLeftRequest(self.world.player)
            self.event_manager.post(ev)
        elif (event.input.type == pygame.KEYUP and event.action == Actions.MOVE_RIGHT):
            ev = events.EntityStopMovingRightRequest(self.world.player)
            self.event_manager.post(ev)
        elif (event.input.type == pygame.KEYDOWN and event.action == Actions.JUMP):
            ev = events.EntityJumpRequest(self.world.player)
            self.event_manager.post(ev)
        #Keys + aiming
        elif ((event.input.type == pygame.KEYDOWN or event.input.type == pygame.KEYUP)
               and is_aim_action(event.action)):
            self.handle_keys_aiming(event)
        #Joystick button + movement
        elif (input_is_a_joystickbutton(event.input) and event.action == Actions.MOVE_LEFT):
            if (event.input.type == pygame.JOYBUTTONDOWN):
                ev = events.EntityMovesLeftRequest(self.world.player)
                self.event_manager.post(ev)
            elif (event.input.type == pygame.JOYBUTTONUP):
                ev = events.EntityStopMovingLeftRequest(self.world.player)
                self.event_manager.post(ev)
        elif (input_is_a_joystickbutton(event.input) and event.action == Actions.MOVE_RIGHT):
            if (event.input.type == pygame.JOYBUTTONDOWN):
                ev = events.EntityMovesRightRequest(self.world.player)
                self.event_manager.post(ev)
            elif (event.input.type == pygame.JOYBUTTONUP):
                ev = events.EntityStopMovingRightRequest(self.world.player)
                self.event_manager.post(ev)
        elif (input_is_a_joystickbutton(event.input) and event.action == Actions.JUMP):
            if (event.input.type == pygame.JOYBUTTONDOWN):
                ev = events.EntityJumpRequest(self.world.player)
                self.event_manager.post(ev)
        #Joystick button + aiming
        elif ((event.input.type == pygame.JOYBUTTONDOWN or event.input.type == pygame.JOYBUTTONUP)
               and is_aim_action(event.action)):
            self.handle_keys_aiming(event)
        #Joystick axis + aiming
        elif (event.input.type == pygame.JOYAXISMOTION and is_aim_action(event.action)):
            self.handle_axis_aiming(event)
        #Joystick axis + moving
        elif (event.input.type == pygame.JOYAXISMOTION and event.action == Actions.MOVE_LEFT):
            offset = 0.5
            value = event.input.value
            if abs(value) > offset:
                ev = events.EntityMovesLeftRequest(self.world.player)
            else:
                ev = events.EntityStopMovingLeftRequest(self.world.player)
            self.event_manager.post(ev)
        elif (event.input.type == pygame.JOYAXISMOTION and event.action == Actions.MOVE_RIGHT):
            offset = 0.5
            value = event.input.value
            if abs(value) > offset:
                ev = events.EntityMovesRightRequest(self.world.player)
            else:
                ev = events.EntityStopMovingRightRequest(self.world.player)
            self.event_manager.post(ev)
        elif (event.input.type == pygame.JOYAXISMOTION and event.action == Actions.JUMP):
            offset = 0.5
            value = event.input.value
            if abs(value) > offset:
                ev = events.EntityJumpRequest(self.world.player)
                self.event_manager.post(ev)
        #Joystick hat + aiming
        elif (event.input.type == pygame.JOYHATMOTION and is_aim_action(event.action)):
            self.handle_hat_aiming(event)
        #Joystick hat + moving
        elif (event.input.type == pygame.JOYHATMOTION and is_movement_action(event.action)):
            x_value, y_value = event.input.value
            if (x_value < 0):
                ev = events.EntityMovesLeftRequest(self.world.player)
                self.event_manager.post(ev)
            elif (x_value > 0):
                ev = events.EntityMovesRightRequest(self.world.player)
                self.event_manager.post(ev)
            else:
                ev = events.EntityStopMovingLeftRequest(self.world.player)
                self.event_manager.post(ev)
                ev = events.EntityStopMovingRightRequest(self.world.player)
                self.event_manager.post(ev)
            if (y_value > 0):
                ev = events.EntityJumpRequest(self.world.player)
                self.event_manager.post(ev)

    def handle_keys_aiming(self, event):
        if event.input.type == pygame.KEYDOWN or event.input.type == pygame.JOYBUTTONDOWN:
            if event.action == Actions.AIM_Y and not self.key_down:
                self.key_up = True
            elif event.action == Actions.AIM_MINUS_Y and not self.key_up:
                self.key_down = True
            elif event.action == Actions.AIM_MINUS_X and not self.key_right:
                self.key_left = True
            elif event.action == Actions.AIM_X and not self.key_left:
                self.key_right = True
        elif event.input.type == pygame.KEYUP or event.input.type == pygame.JOYBUTTONUP:
            if event.action == Actions.AIM_Y:
                self.key_up = False
            elif event.action == Actions.AIM_MINUS_Y:
                self.key_down = False
            elif event.action == Actions.AIM_MINUS_X:
                self.key_left = False
            elif event.action == Actions.AIM_X:
                self.key_right = False

    def handle_axis_aiming(self, event):
        offset = 0.57
        value = event.input.value
        if abs(value) > offset:
            if event.action == Actions.AIM_Y and not self.key_down:
                self.key_up = True
            elif event.action == Actions.AIM_MINUS_Y and not self.key_up:
                self.key_down = True
            elif event.action == Actions.AIM_MINUS_X and not self.key_right:
                self.key_left = True
            elif event.action == Actions.AIM_X and not self.key_left:
                self.key_right = True
        if abs(value) <= offset:
            if event.action == Actions.AIM_Y:
                self.key_up = False
            elif event.action == Actions.AIM_MINUS_Y:
                self.key_down = False
            elif event.action == Actions.AIM_MINUS_X:
                self.key_left = False
            elif event.action == Actions.AIM_X:
                self.key_right = False

    def handle_hat_aiming(self, event):
        x_value, y_value = event.input.value
        self.key_up = y_value > 0
        self.key_down = y_value < 0
        self.key_right = x_value > 0
        self.key_left = x_value < 0

    def handle_arrow_keys(self):
        """Helper Function for aiming with arrow keys"""
        x_axis = 0
        y_axis = 0

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
        if not(x_axis == 0 and y_axis == 0):
            self.handle_attack_request()

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
            self.key_right = False
            self.key_left = False
        else:
            if mouse_x > 0:
                direction_x = 1
                self.key_right = True
            else:
                direction_x = -1
                self.key_left = True
        if epsilon > mouse_y and mouse_y > -epsilon:
            direction_y = 0
            self.key_up = False
            self.key_down = False
        else:
            if mouse_y > 0:
                direction_y = 1
                self.key_up = True
            else:
                direction_y = -1
                self.key_down = True
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
            old_direction = self.world.direction[player_ID] 
            self.world.direction[player_ID] = [x, y]
            if not (old_direction[0] == x and old_direction[1] == y): 
                #Move orb
                self.world.appearance[orb_ID].rect.center = (x*64 + self.world.collider[self.world.player].center[0] ,
                                                            y*64 + self.world.collider[self.world.player].center[1])
                #Save rotation for orbs sprite
                self.world.appearance[orb_ID].angle = angle
                #Rotate hp-ui
                hp_ID = self.world.players[self.world.player].hp_ID
                self.world.appearance[hp_ID].rect.center = self.world.appearance[orb_ID].rect.center
                #self.world.appearance[hp_ID].angle = angle
                ev = events.PlayerAims(self.world.player)
                self.event_manager.post(ev)

    def unpause_game(self):
        '''When game unpauses, send requests, that
        stop player from movement.
        '''
        self.world.game_paused = False
        ev1 = events.EntityStopMovingLeftRequest(self.world.player)
        self.event_manager.post(ev1)
        ev2 = events.EntityStopMovingRightRequest(self.world.player)
        self.event_manager.post(ev2)
        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False
