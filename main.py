import sys
from bidi.algorithm import get_display
from functools import partial
import pygame
import ctypes
from constants import *
from game_over_exceptions import *
from game_counter import Counter
from button import Button
from teams import Teams
from input_box import InputBox
from picture_engine import PictureEngine
from round_score import RoundScore


class Game:
    def __init__(self, width, height):
        self._init_game()
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((width, height))
        self.counter = Counter(GAME_TIME, DOWN_COUNT)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(GAME_FONT, 25)
        self.round_score = RoundScore()
        self.teams = Teams([name_generator(), name_generator()])
        self.round_started = False
        self.picture_engine = PictureEngine("pics", (self.window_width // 2, self.window_height // 2))

    @staticmethod
    def _init_game():
        pygame.init()
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    def cb_success(self):
        self.round_score.inc_score()
        self.round_score.add_word(self.picture_engine.get_picture_title(), True)
        self.picture_engine.next_picture()

    def cb_fail(self):
        self.round_score.add_word(self.picture_engine.get_picture_title(), False)
        self.picture_engine.next_picture()

    def _clear_window(self):
        self.screen.fill(Colors.WHITE)

    def _tick_timer(self, location: list):
        self._clear_window()
        timer = self.font.render(self.counter.get_time_string(), True,
                                 Colors.BLACK if self.counter.time > 10 else Colors.RED)

        width, height = location
        width = width - timer.get_size()[0] * 0.5
        self.screen.blit(timer, (width, height))
        self.counter.tick()
        self.clock.tick(FRAME_RATE)

    def start_round(self, round_number, team):
        self._clear_window()
        self.round_score.reset_round()
        fail_button = Button(self.screen, (self.window_width * 0.35, self.window_height * 0.9), (100, 50), 20,
                             pygame.Color(*Colors.RED), text="Fail",
                             hover_color=pygame.Color(*Colors.LIGHT_RED), cb=self.cb_fail,
                             key_stroke=[pygame.K_LEFT, pygame.K_BACKSPACE, pygame.K_ESCAPE])
        success_button = Button(self.screen, (self.window_width * 0.65, self.window_height * 0.9), (100, 50), 20,
                                pygame.Color(*Colors.GREEN), text="Success",
                                hover_color=pygame.Color(*Colors.LIGHT_GREEN),
                                cb=self.cb_success, key_stroke=[pygame.K_RIGHT, pygame.K_RETURN])

        round_text = self._create_text_obj(f"Round {round_number} | {team}",
                                           (self.window_width * 0.5, self.window_height * 0.1),
                                           color=get_color_from_name(team))

        self.picture_engine.next_picture()

        buttons = [success_button, fail_button]

        while self.round_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(1)
                [button.check_click(event) for button in buttons]
            try:
                self._tick_timer([self.window_width * 0.5, self.window_height * 0.15])
            except TimeoutGameOver:
                # Reset round settings on timeout.
                self.round_started = False
                self.counter.reset()
                self.teams.score[team].append(self.round_score.score)

            # Drawing buttons
            [button.draw_button() for button in buttons]

            picture_title = self.picture_engine.get_picture_title()
            # Image Title
            self.screen.blit(
                *self._create_text_obj(picture_title, (self.window_width * 0.5, self.window_height * 0.25)))
            # Image
            self.picture_engine.draw(self.screen, (self.window_width * 0.5, self.window_height * 0.6))
            # Score
            self._score_table()
            self._display_round_score()
            # Played Words
            self._display_round_words()
            # Round Title
            self.screen.blit(*round_text)

            pygame.display.flip()

    def _create_text_obj(self, text, pos, color=Colors.BLACK, size: int = None, bg_color=None):
        font = self.font
        if size:
            font = pygame.font.Font(GAME_FONT, size)
        text_surface = font.render(get_display(text), True, pygame.Color(*color), bg_color)
        text_rect = text_surface.get_rect(center=pos)

        return text_surface, text_rect

    def _score_table(self):
        def _create_row(x, y, w, h, cols=2):
            cells = []
            for i in range(cols):
                cells.append(pygame.Rect(x + i * w, y, w, h))

            return cells

        row_height = self.window_height * 0.025
        cell_width = self.window_width * 0.08
        start_x = self.window_width * 0.025
        start_y = self.window_height * 0.1

        for idx, team in enumerate(self.teams.teams.keys()):
            color = get_color_from_name(team)
            obj = self._create_text_obj(team, (
                cell_width * idx + start_x + cell_width * 0.5, start_y - self.window_height * 0.025 * 0.5), color=color,
                                        size=20)
            self.screen.blit(*obj)

        for round in range(NUMBER_OF_ROUNDS):
            row = _create_row(start_x, start_y + (round + 1) * row_height, cell_width, row_height)
            for idx, cell in enumerate(row):
                team_scores = list(self.teams.score.values())[idx]
                score = '-'
                if round < len(team_scores):
                    score = str(team_scores[round])
                obj = self._create_text_obj(score, (
                    cell.x + cell_width * 0.5, cell.y + self.window_height * 0.025 * 0.5))
                pygame.draw.rect(self.screen, pygame.Color(*Colors.BLACK), cell, width=1)
                self.screen.blit(*obj)

        sum_row = _create_row(start_x, start_y + (NUMBER_OF_ROUNDS + 1) * row_height, cell_width, row_height)
        for idx, cell in enumerate(sum_row):
            team_scores = list(self.teams.score.values())[idx]
            score = str(sum(team_scores))
            obj = self._create_text_obj(score, (
                cell.x + cell_width * 0.5, cell.y + self.window_height * 0.025 * 0.5))
            pygame.draw.rect(self.screen, pygame.Color(*Colors.BLACK), cell, width=1)
            self.screen.blit(*obj)

    def create_teams(self):
        team_title_text = []
        boxes = {}
        text_obj = []
        start_x = {}
        for idx, team in enumerate(self.teams.teams.keys()):
            color = get_color_from_name(team)
            width = self.window_width * (0.25 + idx*0.5)
            start_x[team] = width
            team_title_text.append(
                self._create_text_obj(team, (width + 70, self.window_height * 0.15), color))
            box = InputBox(width, self.window_height * 0.2, 140, 32)
            boxes[team] = box

        start_button = Button(self.screen, (self.window_width / 2 - 50, self.window_height * 0.9), (100, 50), 15,
                              pygame.Color(*Colors.GRAY), hover_color=pygame.Color(*Colors.LIGHT_GRAY),
                              text="Start Game", cb=self.cb_start_round)

        while not self.round_started:
            self._clear_window()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(1)
                start_button.check_click(event)
                [box.handle_event(event, partial(self.teams.add_team_member, team)) for team, box in boxes.items()]
            [box.draw(self.screen) for box in boxes.values()]
            [self.screen.blit(*txt_team) for txt_team in team_title_text]

            for team_name, members in self.teams.teams.items():

                text_obj = [
                    self._create_text_obj(f"{idx+1}. {member}", (start_x.get(team_name), self.window_height * 0.25 + (idx + 1) * 32)) for
                    idx, member in enumerate(members)]

                [self.screen.blit(*obj) for obj in text_obj]
            start_button.draw_button()
            pygame.draw.line(self.screen, pygame.Color(*Colors.BLACK),
                             (self.window_width * 0.5, self.window_height * 0.15),
                             (self.window_width * 0.5, self.window_height * 0.85))

            pygame.display.flip()

    def cb_start_round(self):
        self.round_started = True

    def display_score(self):
        total_scores = {team_name: sum(scores) for team_name, scores in self.teams.score.items()}
        pos = (self.window_width * 0.5, self.window_height * 0.5)
        if len(list(dict.fromkeys(list(total_scores.values())))) == 1:
            next_up = self._create_text_obj("Draw!", pos, Colors.BLACK, 80)
            self.screen.blit(*next_up)
        else:
            # Show winner
            winners = max(total_scores, key=total_scores.get)
            print(winners)
            print(self.teams.teams.get(winners))
            pos = (self.window_width * 0.5, self.window_height * 0.5)
            next_up = self._create_text_obj(f"{winners} The Winners!", pos, get_color_from_name(winners), 80)
            self.screen.blit(*next_up)
            pos = (pos[0], pos[1] + next_up[0].get_height() * 1.5)
            self.screen.blit(*self._create_text_obj(', '.join(self.teams.teams.get(winners)), pos, get_color_from_name(winners), 60))

    def _display_round_words(self):
        x_pos = self.window_width * 0.9
        y_pos = self.window_height * 0.15
        line_height = 0
        for idx, (word, success) in enumerate(self.round_score.words):
            color = Colors.GREEN if success else Colors.LIGHT_RED
            surface, obj = self._create_text_obj(word, (x_pos, y_pos + line_height * idx), color=color)
            line_height = surface.get_height()
            self.screen.blit(surface, obj)

    def _display_round_score(self):
        x_pos = self.window_width * 0.9
        y_pos = self.window_height * 0.1

        obj = self._create_text_obj(str(self.round_score.score), (x_pos, y_pos), color=Colors.BLUE, bg_color=Colors.LIGHT_GRAY,
                                    size=50)
        self.screen.blit(*obj)

    def _next_up_window(self, team):
        pos = (self.window_width * 0.5, self.window_height * 0.5)
        next_up = self._create_text_obj("Next Up...", pos, Colors.BLACK, 70)
        self.screen.blit(*next_up)
        pos = (pos[0], pos[1] + next_up[0].get_height()*1.5)
        self.screen.blit(*self._create_text_obj(team, pos, get_color_from_name(team), 60))

    def start_game(self):
        end_game = False
        self._clear_window()
        pygame.display.set_caption("Anything Goes")

        start_button = Button(self.screen, (self.window_width / 2 - 50, self.window_height * 0.9), (100, 50), 15,
                              pygame.Color(*Colors.GRAY), hover_color=pygame.Color(*Colors.LIGHT_GRAY),
                              text="Start Round", cb=self.cb_start_round)
        self.create_teams()
        round_counter = 1
        in_round_counter = 0
        teams = list(self.teams.teams.keys())
        while not end_game:
            self._clear_window()
            self._score_table()
            self._display_round_words()
            self._display_round_score()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end_game = True
                start_button.check_click(event)

            team = teams[in_round_counter]

            self._next_up_window(team)

            if self.round_started:
                pygame.display.flip()
                pygame.time.wait(3000)
                team = teams[in_round_counter]
                self.start_round(round_counter, team)
                round_counter = round_counter + in_round_counter
                in_round_counter = (in_round_counter + 1) % 2

            start_button.draw_button()
            self.round_started = False

            if round_counter > NUMBER_OF_ROUNDS:
                self._clear_window()
                self._score_table()
                self.display_score()
                pygame.display.flip()
                pygame.time.wait(9000)
                self.teams = Teams([name_generator(), name_generator()])
                end_game = True

            pygame.display.flip()
        self.start_game()

if __name__ == '__main__':
    user32 = ctypes.windll.user32
    width, height = user32.GetSystemMetrics(16), user32.GetSystemMetrics(17)
    Game(width, height).start_game()
