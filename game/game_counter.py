import pygame
from constants import *
from game_over_exceptions import *

class Counter:
    def __init__(self, start_time: int = 0, direction: bool = UP_COUNT, threshold=60):
        self.start_ticks = pygame.time.get_ticks()
        self.start_time = start_time
        self.time = start_time
        self.direction = direction
        self.threshold = threshold

    def reset(self):
        self.time = self.start_time
        self.start_ticks = pygame.time.get_ticks()

    def _timer_action(self):
        if self.direction == UP_COUNT:
            self.time += 1
        else:
            self.time -= 1
            if self.time <= 0:
                raise TimeoutGameOver()

    def tick(self):
        if self.direction is UP_COUNT:
            self.time = self.start_time + (pygame.time.get_ticks() - self.start_ticks) // 1000
            if self.time >= self.threshold:
                raise TimeoutGameOver()
        else:
            self.time = self.start_time - (pygame.time.get_ticks() - self.start_ticks) // 1000
            if self.time <= self.threshold:
                raise TimeoutGameOver()

    def get_time_string(self):
        minutes = self.time // 60
        seconds = self.time % 60

        return f"{minutes:02}:{seconds:02}"