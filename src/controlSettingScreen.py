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
    AIM_WITH_MOUSE = 8
    MOVE_WITH_HAT = 9
    AIM_WITH_HAT = 10
    USE_DEFAULT_CONTROLS = 11

class ControlSettingScreen():
    def __init__(self, screen):
        self.screen = screen
        self.textPrint = TextPrint()

        self.icon_list = pygame.sprite.Group()
        self.background_image = pygame.image.load("data/ui_settings.png").convert()
        #Selection icon
        self.selectedIm = pygame.sprite.Sprite()
        self.selectedIm.image = pygame.image.load("data/ui_selected.png").convert_alpha()
        self.selectedIm.rect = self.selectedIm.image.get_rect(center = (81, 209))
        self.icon_list.add(self.selectedIm)
        #Jump icon
        self.jumpIm = pygame.sprite.Sprite()
        self.jumpIm.image = pygame.image.load("data/ui_jump.png").convert()
        self.jumpIm.rect = self.jumpIm.image.get_rect(center = (81, 209))
        self.icon_list.add(self.jumpIm)
        #Move Left icon
        self.moveLeftIm = pygame.sprite.Sprite()
        self.moveLeftIm.image = pygame.image.load("data/ui_move_left.png").convert()
        self.moveLeftIm.rect = self.moveLeftIm.image.get_rect(center = (81, 309))
        self.icon_list.add(self.moveLeftIm)
        #Move Right icon
        self.moveRightIm = pygame.sprite.Sprite()
        self.moveRightIm.image = pygame.image.load("data/ui_move_right.png").convert()
        self.moveRightIm.rect = self.moveRightIm.image.get_rect(center = (81, 409))
        self.icon_list.add(self.moveRightIm)
        #Use Hat to Move icon
        self.moveHatIm = pygame.sprite.Sprite()
        self.moveHatIm.image = pygame.image.load("data/ui_move_hat.png").convert()
        self.moveHatIm.rect = self.moveHatIm.image.get_rect(center = (601, 109))
        self.icon_list.add(self.moveHatIm)
        #Use Aim in X direction icon
        self.aimXIm = pygame.sprite.Sprite()
        self.aimXIm.image = pygame.image.load("data/ui_aim_x.png").convert()
        self.aimXIm.rect = self.aimXIm.image.get_rect(center = (341, 109))
        self.icon_list.add(self.aimXIm)
        #Use Aim in -X direction icon
        self.aimMXIm = pygame.sprite.Sprite()
        self.aimMXIm.image = pygame.image.load("data/ui_aim_m_x.png").convert()
        self.aimMXIm.rect = self.aimMXIm.image.get_rect(center = (341, 209))
        self.icon_list.add(self.aimMXIm)
        #Use Aim in Y direction icon
        self.aimYIm = pygame.sprite.Sprite()
        self.aimYIm.image = pygame.image.load("data/ui_aim_y.png").convert()
        self.aimYIm.rect = self.aimYIm.image.get_rect(center = (341, 309))
        self.icon_list.add(self.aimYIm)
        #Use Aim in -Y direction icon
        self.aimMYIm = pygame.sprite.Sprite()
        self.aimMYIm.image = pygame.image.load("data/ui_aim_m_y.png").convert()
        self.aimMYIm.rect = self.aimMYIm.image.get_rect(center = (341, 409))
        self.icon_list.add(self.aimMYIm)
        #Use Mouse to Aim icon
        self.aimMouseIm = pygame.sprite.Sprite()
        self.aimMouseIm.image = pygame.image.load("data/ui_aim_mouse.png").convert()
        self.aimMouseIm.rect = self.aimMouseIm.image.get_rect(center = (601, 309))
        self.icon_list.add(self.aimMouseIm)
        #Use Hat to Aim icon
        self.aimHatIm = pygame.sprite.Sprite()
        self.aimHatIm.image = pygame.image.load("data/ui_aim_hat.png").convert()
        self.aimHatIm.rect = self.aimHatIm.image.get_rect(center = (601, 209))
        self.icon_list.add(self.aimHatIm)
        #Default controls
        self.defaultIm = pygame.sprite.Sprite()
        self.defaultIm.image = pygame.image.load("data/ui_default.png").convert()
        self.defaultIm.rect = self.defaultIm.image.get_rect(center = (601, 409))
        self.icon_list.add(self.defaultIm)
        #Done icon
        self.doneIm = pygame.sprite.Sprite()
        self.doneIm.image = pygame.image.load("data/orb.png").convert()
        self.doneIm.rect = self.doneIm.image.get_rect(center = (570, 560))
        self.icon_list.add(self.doneIm)
        self.currently_selected = SelectedUI.JUMP

        self.disable_move_ctrls = False
        self.disable_aim_ctrls = False

        self.use_hat_to_aim = -1 #index of hat stored here
        self.use_hat_to_move = -1# -1 means, that a hat is not used for this control
        self.use_mouse_to_aim_and_fire = False

    def hit_ui_element(self, (x, y)):
        if (self.jumpIm.image.get_alpha() > 0
            and self.jumpIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.jumpIm.rect.copy()
            self.currently_selected = SelectedUI.JUMP
            return self.currently_selected
        elif (self.moveLeftIm.image.get_alpha() > 0
            and self.moveLeftIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.moveLeftIm.rect.copy()
            self.currently_selected = SelectedUI.MOVE_LEFT
            return self.currently_selected
        elif (self.moveRightIm.image.get_alpha() > 0
            and self.moveRightIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.moveRightIm.rect.copy()
            self.currently_selected = SelectedUI.MOVE_RIGHT
            return self.currently_selected
        elif (self.aimXIm.image.get_alpha() > 0
            and self.aimXIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.aimXIm.rect.copy()
            self.currently_selected = SelectedUI.AIM_X
            return self.currently_selected
        elif (self.aimMXIm.image.get_alpha() > 0
            and self.aimMXIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.aimMXIm.rect.copy()
            self.currently_selected = SelectedUI.AIM_MINUS_X
            return self.currently_selected
        elif (self.aimYIm.image.get_alpha() > 0
            and self.aimYIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.aimYIm.rect.copy()
            self.currently_selected = SelectedUI.AIM_Y
            return self.currently_selected
        elif (self.aimMYIm.image.get_alpha() > 0
            and self.aimMYIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.aimMYIm.rect.copy()
            self.currently_selected = SelectedUI.AIM_MINUS_Y
            return self.currently_selected
        elif (self.aimMouseIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.aimMouseIm.rect.copy()
            self.currently_selected = SelectedUI.AIM_WITH_MOUSE
            return self.currently_selected
        elif (self.aimHatIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.aimHatIm.rect.copy()
            self.currently_selected = SelectedUI.AIM_WITH_HAT
            return self.currently_selected
        elif (self.moveHatIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.moveHatIm.rect.copy()
            self.currently_selected = SelectedUI.MOVE_WITH_HAT
            return self.currently_selected
        elif (self.defaultIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.defaultIm.rect.copy()
            self.currently_selected = SelectedUI.USE_DEFAULT_CONTROLS
            return self.currently_selected
        elif (self.doneIm.image.get_alpha() > 0
            and self.doneIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.doneIm.rect.copy()
            self.currently_selected = SelectedUI.READY
            return self.currently_selected
        else:
            return None
        

    def draw(self):
        """Used for custom controlls initialisation screen
        
        :param dt: CPU tick
        :type dt: int
        """
        self.screen.fill(( 255, 255, 255))
        self.screen.blit(self.background_image, [0, 0])
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

    def deactivate_move_btns(self):
        """Disables UI elements for movement"""
        self.jumpIm.image.set_alpha(0)
        self.moveLeftIm.image.set_alpha(0)
        self.moveRightIm.image.set_alpha(0)

    def activate_move_btns(self):
        """Enable UI elements for movement"""
        self.jumpIm.image.set_alpha(255)
        self.moveLeftIm.image.set_alpha(255)
        self.moveRightIm.image.set_alpha(255)

    def toggle_move_btns(self):
        """Toggle UI elements for movement"""
        self.jumpIm.image.set_alpha(abs(self.jumpIm.image.get_alpha()-255))
        self.moveLeftIm.image.set_alpha(abs(self.moveLeftIm.image.get_alpha()-255))
        self.moveRightIm.image.set_alpha(abs(self.moveRightIm.image.get_alpha()-255))

    def deactivate_aim_btns(self):
        """Disables UI elements for aiming"""
        self.aimMXIm.image.set_alpha(0)
        self.aimMYIm.image.set_alpha(0)
        self.aimXIm.image.set_alpha(0)
        self.aimYIm.image.set_alpha(0)

    def activate_aim_btns(self):
        """Enable UI elements for aiming"""
        self.aimMXIm.image.set_alpha(255)
        self.aimMYIm.image.set_alpha(255)
        self.aimXIm.image.set_alpha(255)
        self.aimYIm.image.set_alpha(255)

    def toggle_aim_btns(self):
        self.aimMXIm.image.set_alpha(abs(self.aimMXIm.image.get_alpha()-255))
        self.aimMYIm.image.set_alpha(abs(self.aimMYIm.image.get_alpha()-255))
        self.aimXIm.image.set_alpha(abs(self.aimXIm.image.get_alpha()-255))
        self.aimYIm.image.set_alpha(abs(self.aimYIm.image.get_alpha()-255))

    def deactivate_mouse_aim_btn(self):
        self.aimMouseIm.image.set_alpha(0)

    def activate_mouse_aim_btn(self):
        self.aimMouseIm.image.set_alpha(255)

    def deactivate_hat_aim_btn(self):
        self.aimHatIm.image.set_alpha(0)

    def activate_hat_aim_btn(self):
        self.aimHatIm.image.set_alpha(255)

    def deactivate_hat_move_btn(self):
        self.moveHatIm.image.set_alpha(0)

    def activate_hat_move_btn(self):
        self.moveHatIm.image.set_alpha(255)
