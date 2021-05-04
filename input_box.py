import pygame
from constants import *
from bidi.algorithm import get_display

class InputBox:
    def __init__(self, x, y, w, h, text='', title=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.Font('Adobe Hebrew Regular.otf', 32)

        self.txt_surface = self.font.render(text, True, pygame.Color(*Colors.BLACK))
        self.active = False

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, pygame.Color(*Colors.LIGHT_GRAY), self.rect, 2)

    def handle_event(self, event, cb=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    if cb:
                        cb(self.text)
                        self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(get_display(self.text), True, pygame.Color(*Colors.BLACK))