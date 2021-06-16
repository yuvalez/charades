import pygame
from constants import *
from bidi.algorithm import get_display

class CheckBox:
    def __init__(self, x, y, size=15, font=None, text='', checked=False):
        self.pos = (x, y)
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.text = text
        if font is None:
            self.font = pygame.font.Font('Adobe Hebrew Regular.otf', 20)
        else:
            self.font = font

        self.txt_surface = self.font.render(get_display(text), True, pygame.Color(*Colors.BLACK))
        self.checked = checked

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.left*0.95 - self.txt_surface.get_width(), self.rect.y))
        pygame.draw.rect(screen, pygame.Color(*Colors.BLACK), self.rect, width=1)

        if self.checked:
            pygame.draw.line(screen, pygame.Color(*Colors.DARK_GRAY),
                             start_pos=(self.rect.left + 2, self.rect.centery), end_pos=(self.rect.centerx - 2, self.rect.bottom-2), width=3)
            pygame.draw.line(screen, pygame.Color(*Colors.DARK_GRAY),
                             start_pos=(self.rect.centerx - 2, self.rect.bottom - 2), end_pos=(self.rect.right+2, self.rect.top - 5), width=3)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked

    def is_checked(self):
        return self.checked

    def get_text(self):
        return self.text