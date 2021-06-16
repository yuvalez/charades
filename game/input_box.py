import pygame
from constants import *
from bidi.algorithm import get_display

DIGITS = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
          pygame.K_9]

class InputBox:
    def __init__(self, x, y, w, h, text='', center=False, text_size=32, only_int=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.Font('Adobe Hebrew Regular.otf', text_size)
        self.center = center
        self.only_int = only_int
        self.txt_surface = self.font.render(text, True, pygame.Color(*Colors.BLACK))
        self.active = False

    def draw(self, screen):
        w = self.rect.x + 5 if not self.center else self.rect.x + self.rect.width / 2
        h = self.rect.y
        screen.blit(self.txt_surface, (w, h))
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
                elif self.only_int:
                    if event.key in DIGITS:
                        self.text += event.unicode
                else:
                    self.text += event.unicode


                self.txt_surface = self.font.render(get_display(self.text), True, pygame.Color(*Colors.BLACK))

    def get_text(self):
        return self.text