#Protected keys: enter, escape
#

import pygame
import events

BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# This is a simple class that will help us print to the screen
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 30)

    def print_(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        width, height = self.font.size(textString);
        self.x += width
        return width

    def println_(self, screen, textString):
        self.print_(screen, textString)
        width, height = self.font.size(textString);
        self.x -= width
        self.line_break()
        return width

    def carriage_return(self, width):
        self.x -= width

    def line_break(self):
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 30
        
    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

class SelectedUI:
    READY = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    JUMP = 3
    AIM_X = 4
    AIM_MINUS_X = 5
    AIM_Y = 6
    AIM_MINUS_Y = 7

class ControlSettingScreen():
    def __init__(self, screen, evManager):
        self.screen = screen
        self.textPrint = TextPrint()

        self.icon_list = pygame.sprite.Group()
        self.selectedIm = pygame.sprite.Sprite()
        self.selectedIm.image = pygame.image.load("data/orb_inverted.png").convert()
        self.selectedIm.rect = self.selectedIm.image.get_rect(center = (30, 30))
        self.icon_list.add(self.selectedIm)
        self.jumpIm = pygame.sprite.Sprite()
        self.jumpIm.image = pygame.image.load("data/orb.png").convert()
        self.jumpIm.rect = self.jumpIm.image.get_rect(center = (30, 30))
        self.icon_list.add(self.jumpIm)
        self.moveLeftIm = pygame.sprite.Sprite()
        self.moveLeftIm.image = pygame.image.load("data/orb.png").convert()
        self.moveLeftIm.rect = self.moveLeftIm.image.get_rect(center = (30, 60))
        self.icon_list.add(self.moveLeftIm)
        self.moveRightIm = pygame.sprite.Sprite()
        self.moveRightIm.image = pygame.image.load("data/orb.png").convert()
        self.moveRightIm.rect = self.moveRightIm.image.get_rect(center = (30, 90))
        self.icon_list.add(self.moveRightIm)
        
        self.doneIm = pygame.sprite.Sprite()
        self.doneIm.image = pygame.image.load("data/orb.png").convert()
        self.doneIm.rect = self.doneIm.image.get_rect(center = (30, 120))
        self.icon_list.add(self.doneIm)
        self.currently_selected = SelectedUI.JUMP

        self.event_manager = evManager
        self.event_manager.register_listener(self)

        self.actions_map = {}
        self.use_hat_to_aim = -1 #index of hat stored here
        self.use_hat_to_move = -1# -1 means, that a hat is not used for this control
        self.use_mouse_to_aim_and_fire = False

        self.action_to_map = 0
        self.current_ui_point = 0

    def hit_ui_element(self, (x, y)):
        if self.jumpIm.rect.collidepoint(x,y):
            self.selectedIm.rect = self.jumpIm.rect.copy()
            self.currently_selected = SelectedUI.JUMP
        elif self.moveLeftIm.rect.collidepoint(x,y):
            self.selectedIm.rect = self.moveLeftIm.rect.copy()
            self.currently_selected = SelectedUI.MOVE_LEFT
        elif self.moveRightIm.rect.collidepoint(x,y):
            self.selectedIm.rect = self.moveRightIm.rect.copy()
            self.currently_selected = SelectedUI.MOVE_RIGHT
        elif self.doneIm.rect.collidepoint(x,y):
            self.selectedIm.rect = self.doneIm.rect.copy()
            self.currently_selected = SelectedUI.READY

    def notify(self, event):
        if hasattr(event, "type"):
            #Toggle mouse input
            #when the corresponding ui point is selected
            if event.type == pygame.MOUSEBUTTONDOWN and self.current_ui_point == 0:
                self.use_mouse_to_aim_and_fire = (not self.use_mouse_to_aim_and_fire)
                self.inc_init_counter()
            if event.type == pygame.JOYHATMOTION:
                if self.current_ui_point == 1 and not event.hat == self.use_hat_to_move:
                    self.use_hat_to_aim = event.hat
                    self.inc_init_counter()
                elif self.current_ui_point == 2 and not event.hat == self.use_hat_to_aim:
                    self.use_hat_to_move = event.hat
                    self.inc_init_counter()
            #BACKSPACE to go one ui point back
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.dec_input_counter()
                elif event.key == pygame.K_RETURN:
                    #Start game with this controlls
                    if self.current_ui_point == 10: #K_RETURN is the enter key
                        self.event_manager.post(events.TogglePauseEvent())
                        if self.use_mouse_to_aim_and_fire:
                            self.remove_aim_controls()
                        elif self.use_hat_to_aim > -1:
                            self.remove_aim_controls()
                            self.event_manager.post(events.ToggleContinuousAttack())
                        else:
                            self.event_manager.post(events.ToggleContinuousAttack())
                        if self.use_hat_to_move > -1:
                            self.remove_movement_controls()
                        ev = events.SetControlls(self.actions_map, self.use_hat_to_aim,
                                                 self.use_hat_to_move, self.use_mouse_to_aim_and_fire)
                        self.event_manager.post(ev)
                    #Or go one ui point further
                    else:
                        self.inc_init_counter()
            if (not self.key_used(event)):
                self.save_key(event)

        if isinstance(event, events.TickEvent):
            self.draw()

    def key_used(self, control):
        """Is control already mapped to action.
        """
        for value in self.actions_map.itervalues():
            if equal_input_source(control, value):
                return True
        return False

    def save_key(self, event):
        """Save input to an action.
        """
        if self.action_to_map > 0 and self.action_to_map < 8:
            if (event.type == pygame.JOYBUTTONDOWN or
                event.type == pygame.JOYAXISMOTION or
                event.type == pygame.KEYDOWN):
                if event.type == pygame.KEYDOWN:
                    if not(event.key == pygame.K_BACKSPACE or
                           event.key == pygame.K_ESCAPE or
                           event.key == pygame.K_RETURN):
                        self.actions_map[self.action_to_map] = event
                        self.inc_init_counter()
                elif event.type == pygame.JOYAXISMOTION:
                    if abs(event.value) > 0.5:
                        self.actions_map[self.action_to_map] = event
                        self.inc_init_counter()
                else:
                    self.actions_map[self.action_to_map] = event
                    self.inc_init_counter()

    def remove_aim_controls(self):
        '''Remove all aim controls from action_map.
        '''
        to_remove = list()
        for action in self.actions_map.iterkeys():
            if is_aim_action(action):
                to_remove.append(action)
        for r in to_remove:
            del self.actions_map[r]

    def remove_movement_controls(self):
        '''Remove all movement controls from action_map.
        '''
        to_remove = list()
        for action in self.actions_map.iterkeys():
            if is_movement_action(action):
                to_remove.append(action)
        for r in to_remove:
            del self.actions_map[r]

    def inc_init_counter(self):
        """Helper for actions counter.
        """
        amount_to_skip = 0
        limit = 0
        if self.use_mouse_to_aim_and_fire or self.use_hat_to_aim > -1:
            amount_to_skip = 4
            limit = 5
        if self.use_hat_to_move > -1:
            amount_to_skip = 3
            limit = 2
        if self.use_hat_to_move > -1 and (self.use_mouse_to_aim_and_fire or self.use_hat_to_aim > -1):
            amount_to_skip = 7
            limit = 2
        if self.current_ui_point == limit:
            self.current_ui_point += amount_to_skip
        if self.current_ui_point > 10:
            self.current_ui_point = 0
        else:
            self.current_ui_point += 1
        #update action that is currently mapped
        if (self.current_ui_point-2) < 8 and (self.current_ui_point-2) > 0:
            self.action_to_map = (self.current_ui_point-2)
        else:
            self.action_to_map = 0

    def dec_input_counter(self):
        """Helper for actions counter.
        """
        amount_to_skip = 0
        limit = 0
        if self.use_mouse_to_aim_and_fire or self.use_hat_to_aim > -1:
            amount_to_skip = 4
            limit = 10
        if self.use_hat_to_move > -1:
            amount_to_skip = 3
            limit = 6
        if self.use_hat_to_move > -1 and (self.use_mouse_to_aim_and_fire or self.use_hat_to_aim > -1):
            amount_to_skip = 7
            limit = 10
        if self.current_ui_point == limit:
            self.current_ui_point -= amount_to_skip
        if self.current_ui_point > 0:
            self.current_ui_point -= 1
        else:
            self.current_ui_point = 10

        if (self.current_ui_point-2) < 8 and (self.current_ui_point-2) > 0:
            self.action_to_map = (self.current_ui_point-2)
        else:
            self.action_to_map = 0

    def draw(self):
        """Used for custom controlls initialisation screen
        
        :param dt: CPU tick
        :type dt: int
        """
        self.screen.fill(( 255, 255, 255))
        # Copy image to screen:
        self.icon_list.draw(self.screen)
        pygame.display.flip()

        '''
        self.screen.fill(WHITE)
        self.textPrint.reset()
        self.textPrint.println_(self.screen, "Control settings")
        self.textPrint.line_break()
        self.textPrint.println_(self.screen, "Press 'enter' to move point further or")
        self.textPrint.println_(self.screen, "'backspace' to move back.")
        self.textPrint.println_(self.screen, "Press 'enter' on 'Use this layout?' to start.")
        self.textPrint.line_break()
        
        w = self.textPrint.print_(self.screen, "Use Mouse to fire and aim: ")
        w += self.print_key_layout(0)
        self.textPrint.carriage_return(w)
        self.textPrint.line_break()
        w = self.textPrint.print_(self.screen, "Use Hat to fire and aim: ")
        w += self.print_key_layout(1)
        self.textPrint.carriage_return(w)
        self.textPrint.line_break()
        w = self.textPrint.print_(self.screen, "Use Hat to move: ")
        w += self.print_key_layout(2)
        self.textPrint.carriage_return(w)
        self.textPrint.line_break()
        if (self.use_hat_to_move > -1):
            self.textPrint.println_(self.screen, "Move Left: -")
            self.textPrint.println_(self.screen, "Move Right: -")
            self.textPrint.println_(self.screen, "Jump: -")
        else:
            w = self.textPrint.print_(self.screen, "Move Left: ")
            w += self.print_key_layout(3)
            self.textPrint.carriage_return(w)
            self.textPrint.line_break()
            w = self.textPrint.print_(self.screen, "Move Right: ")
            w += self.print_key_layout(4)
            self.textPrint.carriage_return(w)
            self.textPrint.line_break()
            w = self.textPrint.print_(self.screen, "Jump: ")
            w += self.print_key_layout(5)
            self.textPrint.carriage_return(w)
            self.textPrint.line_break()
        if (self.use_mouse_to_aim_and_fire or self.use_hat_to_aim > -1):
            self.textPrint.println_(self.screen, "Aim in x direction: -")
            self.textPrint.println_(self.screen, "Aim in -x direction: -")
            self.textPrint.println_(self.screen, "Aim in y direction: -")
            self.textPrint.println_(self.screen, "Aim in -y direction: -")
        else:
            w = self.textPrint.print_(self.screen, "Aim in x direction: ")
            w += self.print_key_layout(6)
            self.textPrint.carriage_return(w)
            self.textPrint.line_break()
            w = self.textPrint.print_(self.screen, "Aim in -x direction: ")
            w += self.print_key_layout(7)
            self.textPrint.carriage_return(w)
            self.textPrint.line_break()
            w = self.textPrint.print_(self.screen, "Aim in y direction: ")
            w += self.print_key_layout(8)
            self.textPrint.carriage_return(w)
            self.textPrint.line_break()
            w = self.textPrint.print_(self.screen, "Aim in -y direction: ")
            w += self.print_key_layout(9)
            self.textPrint.carriage_return(w)
            self.textPrint.line_break()
        w = self.textPrint.print_(self.screen, "Use this Layout?")
        w += self.print_key_layout(10)
        pygame.display.flip()
        '''

    def print_key_layout(self, action_index):
        """Shows action to key mapping and which action to map as next.
        """
        w = 0
        if action_index == 0:
            w += self.textPrint.print_(self.screen, "{} (press a mouse button to toggle)".format(self.use_mouse_to_aim_and_fire))
        elif action_index == 1:
            w += self.textPrint.print_(self.screen, "{} (press a hat to toggle)".format(self.use_hat_to_aim))
        elif action_index == 2:
            w += self.textPrint.print_(self.screen, "{} (press a hat to toggle)".format(self.use_hat_to_move))
        if (action_index-2) in self.actions_map: #it is with offset
            i_index = action_index-2
            type = self.actions_map[i_index].type
            if pygame.JOYBUTTONDOWN == type:
                w += self.textPrint.print_(self.screen, "Button: {}, Joystick: {}".format(self.actions_map[i_index].button,
                                            self.actions_map[i_index].joy))
            elif pygame.JOYAXISMOTION == type:
                w += self.textPrint.print_(self.screen, "Axis: {}, Joystick: {}".format(self.actions_map[i_index].axis,
                                            self.actions_map[i_index].joy))
            elif pygame.KEYDOWN == type:
                w += self.textPrint.print_(self.screen, "Button: {}".format(pygame.key.name(self.actions_map[i_index].key)))
        if self.current_ui_point == action_index: #Current point to set
            if action_index == 10:
                w += self.textPrint.print_(self.screen, "   press enter to start   <----")
            else:
                w += self.textPrint.print_(self.screen, "  <----")
        return w