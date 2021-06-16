import pygame
from constants import *


class Button:
    def __init__(self, screen, position, button_size, font_size, color, text=None, hover_color=None, cb=None,
                 key_stroke: list = None):
        self.__screen = screen
        self.__x, self.__y = position
        self.__w, self.__h = button_size
        self.__color = color
        self.__hover_color = hover_color or color
        self.__font = pygame.font.Font("Adobe Hebrew Regular.otf", font_size)
        self.__callback = cb
        self.__text = text
        self.key_stroke = key_stroke

    def draw_button(self):
        x, y = pygame.mouse.get_pos()
        in_button = self.__x + self.__w > x > self.__x and self.__y + self.__h > y > self.__y
        if in_button:
            pygame.draw.rect(self.__screen, self.__hover_color, (self.__x, self.__y, self.__w, self.__h),
                             border_radius=10)
        else:
            pygame.draw.rect(self.__screen, self.__color, (self.__x, self.__y, self.__w, self.__h), border_radius=10)

        text = self.__font.render(self.__text, True, Colors.BLACK)
        text_rect = text.get_rect(center=(self.__x + self.__w / 2, self.__y + self.__h / 2))
        self.__screen.blit(text, text_rect)

    def check_click(self, event):
        x, y = pygame.mouse.get_pos()
        in_button = self.__x + self.__w > x > self.__x and self.__y + self.__h > y > self.__y
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(3)[0] and in_button and self.__callback:
            self.__callback()
        elif self.key_stroke and event.type == pygame.KEYDOWN and event.key in self.key_stroke and self.__callback:
            self.__callback()
