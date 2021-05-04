
from constants import *
from game_over_exceptions import *

class Counter:
    def __init__(self, start_time: int = 0, direction: bool = UP_COUNT, frame_rate=60):
        self.start_time = start_time
        self.time = start_time
        self.direction = direction
        self.frame_rate = frame_rate
        self.frame_count = 0

    def reset(self):
        self.time = self.start_time
        self.frame_count = 0

    def _timer_action(self):
        if self.direction == UP_COUNT:
            self.time += 1
        else:
            self.time -= 1
            if self.time <= 0:
                raise TimeoutGameOver()

    def tick(self):
        self.frame_count += 1
        if self.frame_count % self.frame_rate == 0:
            self.frame_count = 0
            self._timer_action()

    def get_time_string(self):
        minutes = self.time // 60
        seconds = self.time % 60

        return f"{minutes:02}:{seconds:02}"