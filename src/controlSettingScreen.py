"""
.. module:: controlSettingScreen
    :platform: Unix, Windows
    :synopsis: Graphical representation of the setting screen.
"""

import pygame
import events

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LILAC = (166, 161, 195)
RED = (250, 101, 101)

def move_to(rect, (x, y)):
    """Move the rectangle rect to the point (x,y) so, 
    that rectangles center is centered an (x,y)"""
    rect.move_ip(-rect.x, -rect.y)
    rect.move_ip(x-rect.width/2, y-rect.height/2)

class SelectedUI:
    """UI elements. Actions should be equivalent number as controller.Actions
    """
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
    """Contains UI elements.

    :Attributes:
        - *screen* (pygame.Surface): where this will be drawn
        - *font* (pygame.font.Font): default font (here FreeSans 16)
        - *font_small* (pygame.font.Font): smaller version of the font
        - *textList* : Array with assigned inputs as Strings
        - *icon_list* (pygame.sprite.Group): stores UI sprites
        - *background_image* (pygame.Surface): actually has disabled UI elements drawn on it
    """
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("data/FreeSans.ttf", 16)
        self.font_small = pygame.font.Font("data/FreeSans.ttf", 12)
        self.textList = ["Start game with this settings", #Text on Done button
                         "-", #move left input
                         "-", #move right input
                         "-", #jump input
                         "-", #aim x input
                         "-", #aim -x input
                         "-", #aim y input
                         "-", #aim -y input
                         "No", #aim with mouse
                         "No", #move with hat
                         "No", #aim with hat
                         "No"] #use default control
        self.icon_list = pygame.sprite.Group()
        self.background_image = pygame.image.load("data/ui_settings.png").convert()
        #Selection icon
        self.selectedIm = pygame.sprite.Sprite()
        self.selectedIm.image = pygame.image.load("data/ui_selected.png").convert_alpha()
        self.selectedIm.rect = self.selectedIm.image.get_rect(center = (590, 399)) #default controls
        self.icon_list.add(self.selectedIm)
        #Jump icon
        self.jumpIm = pygame.sprite.Sprite()
        self.jumpIm.image = pygame.image.load("data/ui_jump.png").convert()
        self.jumpIm.rect = self.jumpIm.image.get_rect(center = (70, 199))
        self.icon_list.add(self.jumpIm)
        #Move Left icon
        self.moveLeftIm = pygame.sprite.Sprite()
        self.moveLeftIm.image = pygame.image.load("data/ui_move_left.png").convert()
        self.moveLeftIm.rect = self.moveLeftIm.image.get_rect(center = (70, 299))
        self.icon_list.add(self.moveLeftIm)
        #Move Right icon
        self.moveRightIm = pygame.sprite.Sprite()
        self.moveRightIm.image = pygame.image.load("data/ui_move_right.png").convert()
        self.moveRightIm.rect = self.moveRightIm.image.get_rect(center = (70, 399))
        self.icon_list.add(self.moveRightIm)
        #Use Hat to Move icon
        self.moveHatIm = pygame.sprite.Sprite()
        self.moveHatIm.image = pygame.image.load("data/ui_move_hat.png").convert()
        self.moveHatIm.rect = self.moveHatIm.image.get_rect(center = (590, 99))
        self.icon_list.add(self.moveHatIm)
        self.deactivate_hat_move_btn()
        #Use Aim in X direction icon
        self.aimXIm = pygame.sprite.Sprite()
        self.aimXIm.image = pygame.image.load("data/ui_aim_x.png").convert()
        self.aimXIm.rect = self.aimXIm.image.get_rect(center = (330, 99))
        self.icon_list.add(self.aimXIm)
        #Use Aim in -X direction icon
        self.aimMXIm = pygame.sprite.Sprite()
        self.aimMXIm.image = pygame.image.load("data/ui_aim_m_x.png").convert()
        self.aimMXIm.rect = self.aimMXIm.image.get_rect(center = (330, 199))
        self.icon_list.add(self.aimMXIm)
        #Use Aim in Y direction icon
        self.aimYIm = pygame.sprite.Sprite()
        self.aimYIm.image = pygame.image.load("data/ui_aim_y.png").convert()
        self.aimYIm.rect = self.aimYIm.image.get_rect(center = (330, 299))
        self.icon_list.add(self.aimYIm)
        #Use Aim in -Y direction icon
        self.aimMYIm = pygame.sprite.Sprite()
        self.aimMYIm.image = pygame.image.load("data/ui_aim_m_y.png").convert()
        self.aimMYIm.rect = self.aimMYIm.image.get_rect(center = (330, 399))
        self.icon_list.add(self.aimMYIm)
        #Use Mouse to Aim icon
        self.aimMouseIm = pygame.sprite.Sprite()
        self.aimMouseIm.image = pygame.image.load("data/ui_aim_mouse.png").convert()
        self.aimMouseIm.rect = self.aimMouseIm.image.get_rect(center = (590, 299))
        self.icon_list.add(self.aimMouseIm)
        self.deactivate_mouse_aim_btn()
        #Use Hat to Aim icon
        self.aimHatIm = pygame.sprite.Sprite()
        self.aimHatIm.image = pygame.image.load("data/ui_aim_hat.png").convert()
        self.aimHatIm.rect = self.aimHatIm.image.get_rect(center = (590, 199))
        self.icon_list.add(self.aimHatIm)
        self.deactivate_hat_aim_btn()
        #Default controls
        self.defaultIm = pygame.sprite.Sprite()
        self.defaultIm.image = pygame.image.load("data/ui_default.png").convert()
        self.defaultIm.rect = self.defaultIm.image.get_rect(center = (590, 399))
        self.icon_list.add(self.defaultIm)
        #Done icon
        self.doneIm = pygame.sprite.Sprite()
        self.doneIm.image = pygame.Surface([214, 64])
        self.doneIm.image.fill(RED)
        self.doneIm.image.set_alpha(0)
        self.doneIm.rect = self.doneIm.image.get_rect(center = (666, 522))
        self.icon_list.add(self.doneIm)
        self.currently_selected = SelectedUI.USE_DEFAULT_CONTROLS

    def hit_ui_element(self, (x, y)):
        """Returns enum of hit UI element or none if mouse hits no UI.
    
        :param (x, y): mouse position in pixel on screen
        :rtype: SelectedUI
        """
        if (self.jumpIm.image.get_alpha() > 0
            and self.jumpIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.jumpIm.rect.center)
            self.currently_selected = SelectedUI.JUMP
            return self.currently_selected
        elif (self.moveLeftIm.image.get_alpha() > 0
            and self.moveLeftIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.moveLeftIm.rect.center)
            self.currently_selected = SelectedUI.MOVE_LEFT
            return self.currently_selected
        elif (self.moveRightIm.image.get_alpha() > 0
            and self.moveRightIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.moveRightIm.rect.center)
            self.currently_selected = SelectedUI.MOVE_RIGHT
            return self.currently_selected
        elif (self.aimXIm.image.get_alpha() > 0
            and self.aimXIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.aimXIm.rect.center)
            self.currently_selected = SelectedUI.AIM_X
            return self.currently_selected
        elif (self.aimMXIm.image.get_alpha() > 0
            and self.aimMXIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.aimMXIm.rect.center)
            self.currently_selected = SelectedUI.AIM_MINUS_X
            return self.currently_selected
        elif (self.aimYIm.image.get_alpha() > 0
            and self.aimYIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.aimYIm.rect.center)
            self.currently_selected = SelectedUI.AIM_Y
            return self.currently_selected
        elif (self.aimMYIm.image.get_alpha() > 0
            and self.aimMYIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.aimMYIm.rect.center)
            self.currently_selected = SelectedUI.AIM_MINUS_Y
            return self.currently_selected
        elif (self.aimMouseIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.aimMouseIm.rect.center)
            self.currently_selected = SelectedUI.AIM_WITH_MOUSE
            return self.currently_selected
        elif (self.aimHatIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.aimHatIm.rect.center)
            self.currently_selected = SelectedUI.AIM_WITH_HAT
            return self.currently_selected
        elif (self.moveHatIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.moveHatIm.rect.center)
            self.currently_selected = SelectedUI.MOVE_WITH_HAT
            return self.currently_selected
        elif (self.defaultIm.rect.collidepoint(x,y)):
            move_to(self.selectedIm.rect, self.defaultIm.rect.center)
            self.currently_selected = SelectedUI.USE_DEFAULT_CONTROLS
            self.toggle_default_btn()
            return self.currently_selected
        elif (self.doneIm.rect.collidepoint(x,y)):
            self.selectedIm.rect = self.doneIm.rect.copy()
            self.currently_selected = SelectedUI.READY
            return self.currently_selected
        else:
            return None

    def draw(self):
        """Draw this screen
        """
        self.screen.fill(WHITE)
        self.screen.blit(self.background_image, [0, 0])
        self.icon_list.draw(self.screen)

        self.print_ui_element_names()
        self.print_input_layout()

        pygame.display.flip()

    def print_ui_element_names(self):
        """Print all text of the UI, that is unchangeable.
        """
        text = self.font.render("Control Settings", True, RED)
        self.screen.blit(text, [55, 35])
        text = self.font.render("* make sure all movement and", True, LILAC)
        self.screen.blit(text, [40, 55])
        text = self.font.render("aim directions are assigned", True, LILAC)
        self.screen.blit(text, [40, 70])
        text = self.font.render("* select first the action and hit", True, LILAC)
        self.screen.blit(text, [40, 90])
        text = self.font.render("desired input afterwards", True, LILAC)
        self.screen.blit(text, [40, 105])
        text = self.font.render("* ESC is to exit the game", True, LILAC)
        self.screen.blit(text, [40, 125])
        #
        text = self.font.render("Default Control Settings", True, RED)
        self.screen.blit(text, [55, 490])
        text = self.font.render("Move with A, W, D keys", True, LILAC)
        self.screen.blit(text, [40, 510])
        text = self.font.render("Aim with mouse and attack on click", True, LILAC)
        self.screen.blit(text, [40, 525])
        #
        text = self.font.render("Jump", True, LILAC)
        self.screen.blit(text, [120, 175])
        text = self.font.render("Move Left", True, LILAC)
        self.screen.blit(text, [120, 275])
        text = self.font.render("Move Right", True, LILAC)
        self.screen.blit(text, [120, 375])
        #
        text = self.font.render("Aim X", True, LILAC)
        self.screen.blit(text, [380, 75])
        text = self.font.render("Aim -X", True, LILAC)
        self.screen.blit(text, [380, 175])
        text = self.font.render("Aim Y", True, LILAC)
        self.screen.blit(text, [380, 275])
        text = self.font.render("Aim -Y", True, LILAC)
        self.screen.blit(text, [380, 375])
        #
        text = self.font.render("use Hat to Move", True, LILAC)
        self.screen.blit(text, [640, 75])
        text = self.font.render("use Hat to Aim", True, LILAC)
        self.screen.blit(text, [640, 175])
        text = self.font.render("use Mouse to Aim", True, LILAC)
        self.screen.blit(text, [640, 275])
        text = self.font.render("use Default settings", True, LILAC)
        self.screen.blit(text, [640, 375])
        #
        text = self.font.render("use this settings & play", True, RED)
        self.screen.blit(text, [579, 510])

    def update_input_layout(self, actions_map,
                            use_mouse_to_aim_and_fire, use_hat_to_aim,
                            use_hat_to_move, use_default_controls):
        """Update UI text with assigned input controls.
        
        :param actions_map: actions as controller.Actions mapped to pygame events.
        :type vector: dictionary
        :param use_mouse_to_aim_and_fire: boolean
        :param use_hat_to_aim: index of used hat or -1 if none
        :param use_hat_to_move: index of used hat or -1 if none
        :param use_default_controls: boolean
        """
        for action, control in actions_map.iteritems():
            if (control.type == pygame.KEYDOWN):
                self.textList[action] = "Button: {}".format(pygame.key.name(control.key))
            elif (control.type == pygame.JOYBUTTONDOWN):
                self.textList[action] = "Button: {}, Gamepad: {}".format(control.button, control.joy)
            elif (control.type == pygame.JOYAXISMOTION):
                self.textList[action] = "Axis: {}, Gamepad: {}".format(control.axis, control.joy)
        if use_mouse_to_aim_and_fire:
            self.textList[SelectedUI.AIM_WITH_MOUSE] = "Yes"
        else:
            self.textList[SelectedUI.AIM_WITH_MOUSE] = "No"
        if use_hat_to_aim > -1:
            self.textList[SelectedUI.AIM_WITH_HAT] = "Hat: {}".format(use_hat_to_aim)
        else:
            self.textList[SelectedUI.AIM_WITH_HAT] = "-"
        if use_hat_to_move > -1:
            self.textList[SelectedUI.MOVE_WITH_HAT] = "Hat: {}".format(use_hat_to_move)
        else:
            self.textList[SelectedUI.MOVE_WITH_HAT] = "-"
        if use_default_controls:
            self.textList[SelectedUI.USE_DEFAULT_CONTROLS] = "Yes"
        else:
            self.textList[SelectedUI.USE_DEFAULT_CONTROLS] = "No"

    def print_input_layout(self):
        """Print input layout.
        """
        text = self.font_small.render(self.textList[SelectedUI.JUMP], True, RED)
        self.screen.blit(text, [127, 213])
        text = self.font_small.render(self.textList[SelectedUI.MOVE_LEFT], True, RED)
        self.screen.blit(text, [127, 313])
        text = self.font_small.render(self.textList[SelectedUI.MOVE_RIGHT], True, RED)
        self.screen.blit(text, [127, 413])
        #
        text = self.font_small.render(self.textList[SelectedUI.AIM_X], True, RED)
        self.screen.blit(text, [387, 113])
        text = self.font_small.render(self.textList[SelectedUI.AIM_MINUS_X], True, RED)
        self.screen.blit(text, [387, 213])
        text = self.font_small.render(self.textList[SelectedUI.AIM_Y], True, RED)
        self.screen.blit(text, [387, 313])
        text = self.font_small.render(self.textList[SelectedUI.AIM_MINUS_Y], True, RED)
        self.screen.blit(text, [387, 413])
        #
        text = self.font_small.render(self.textList[SelectedUI.MOVE_WITH_HAT], True, RED)
        self.screen.blit(text, [647, 113])
        text = self.font_small.render(self.textList[SelectedUI.AIM_WITH_HAT], True, RED)
        self.screen.blit(text, [647, 213])
        text = self.font_small.render(self.textList[SelectedUI.AIM_WITH_MOUSE], True, RED)
        self.screen.blit(text, [647, 313])
        text = self.font_small.render(self.textList[SelectedUI.USE_DEFAULT_CONTROLS], True, RED)
        self.screen.blit(text, [647, 413])

    def deactivate_move_btns(self):
        """Disables/Hide UI elements for movement"""
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
        """Disables/Hide UI elements for aiming"""
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
        """Toggle UI elements for aiming."""
        self.aimMXIm.image.set_alpha(abs(self.aimMXIm.image.get_alpha()-255))
        self.aimMYIm.image.set_alpha(abs(self.aimMYIm.image.get_alpha()-255))
        self.aimXIm.image.set_alpha(abs(self.aimXIm.image.get_alpha()-255))
        self.aimYIm.image.set_alpha(abs(self.aimYIm.image.get_alpha()-255))

    def deactivate_mouse_aim_btn(self):
        """Deactivate/Hide UI element for aiming with mouse"""
        self.aimMouseIm.image.set_alpha(0)

    def activate_mouse_aim_btn(self):
        """Enable UI element for aiming with mouse"""
        self.aimMouseIm.image.set_alpha(255)

    def toggle_mouse_aim_btn(self):
        """Toggle UI element for aiming with mouse"""
        self.aimMouseIm.image.set_alpha(abs(self.aimMouseIm.image.get_alpha()-255))

    def deactivate_hat_aim_btn(self):
        """Deactivate/Hide UI element for aiming with hat"""
        self.aimHatIm.image.set_alpha(0)

    def activate_hat_aim_btn(self):
        """Enable UI element for aiming with hat"""
        self.aimHatIm.image.set_alpha(255)

    def deactivate_hat_move_btn(self):
        """Deactivate/Hide UI element for movement with hat"""
        self.moveHatIm.image.set_alpha(0)

    def activate_hat_move_btn(self):
        """Enable UI element for movement with hat"""
        self.moveHatIm.image.set_alpha(255)

    def toggle_default_btn(self):
        """Toggle UI element for default controls"""
        self.defaultIm.image.set_alpha(abs(self.defaultIm.image.get_alpha()-255))

