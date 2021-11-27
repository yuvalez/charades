import sys
import os
from gtts import gTTS
from bidi.algorithm import get_display
from playsound import playsound
from functools import partial
import pygame
import ctypes

from checkbox_group import CheckboxGroup
from constants import *
from game_over_exceptions import *
from game_counter import Counter
from button import Button
from teams import Teams
from input_box import InputBox
from picture_engine import PictureEngine
from round_score import RoundScore


class Game:
    def __init__(self, width, height, path="pics"):
        self._init_game()
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(GAME_FONT, 25)
        self.round_score = RoundScore()
        self.teams = Teams(2)
        self.round_started = False
        self.path = path
        self.number_of_rounds = NUMBER_OF_ROUNDS
        self.game_time = GAME_TIME
        self.accept_failure = False
        self.categories = CheckboxGroup(os.listdir(self.path), (self.window_width * 0.1, self.window_height * 0.45), 15)
        self.picture_engine = PictureEngine(self.path, (self.window_width // 2, self.window_height // 2))

    @staticmethod
    def _init_game():
        pygame.init()
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    def cb_success(self, accept_failure_counter):
        self.round_score.inc_score()
        self.round_score.add_word(self.picture_engine.get_picture_title(), True)
        self.picture_engine.next_picture()
        self.accept_failure = False
        accept_failure_counter.reset()

    def cb_fail(self, accept_failure_counter):
        self.round_score.add_word(self.picture_engine.get_picture_title(), False)
        self.picture_engine.next_picture()
        self.accept_failure = False
        accept_failure_counter.reset()

    def _clear_window(self):
        self.screen.fill(Colors.WHITE)

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

        for round in range(self.number_of_rounds):
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

        sum_row = _create_row(start_x, start_y + (self.number_of_rounds + 1) * row_height, cell_width, row_height)
        for idx, cell in enumerate(sum_row):
            team_scores = list(self.teams.score.values())[idx]
            score = str(sum(team_scores))
            obj = self._create_text_obj(score, (
                cell.x + cell_width * 0.5, cell.y + self.window_height * 0.025 * 0.5))
            pygame.draw.rect(self.screen, pygame.Color(*Colors.BLACK), cell, width=1)
            self.screen.blit(*obj)

    def cb_start_round(self):
        self.round_started = True

    def cb_start_game(self, get_number_of_rounds, get_game_time):
        try:
            self.number_of_rounds = int(get_number_of_rounds())
        except Exception as e:
            print(e)

        try:
            self.game_time = int(get_game_time())
        except Exception as e:
            print(e)
        self.cb_start_round()

    def _game_over(self):
        self._clear_window()
        pos = (self.window_width * 0.5, self.window_height * 0.5)
        next_up = self._create_text_obj("Out of pictures! Sorry...", pos, Colors.BLACK, 80)
        self.screen.blit(*next_up)
        pygame.display.flip()
        pygame.time.wait(1500)

    def display_score(self):
        def _play_draw_sound():
            fp = "draw.mp3"
            try:
                tts = gTTS(f"It's a draw! You losers couldn't win? HAHA! Better luck next time", lang="en")
                tts.save(fp)
                playsound(fp)
            except Exception as e:
                print(type(e).__name__, e)
            finally:
                if os.path.exists(fp):
                    os.remove(fp)

        def _play_victory_sound(team, members):
            fp = "winners.mp3"
            try:
                tts = gTTS(f"{team} are the winners! Well done {', '.join(members)}", lang="en")
                tts.save(fp)
                playsound(fp)
            except Exception as e:
                print(type(e).__name__, e)
            finally:
                if os.path.exists(fp):
                    os.remove(fp)

        total_scores = {team_name: sum(scores) for team_name, scores in self.teams.score.items()}
        pos = (self.window_width * 0.5, self.window_height * 0.5)
        if len(list(dict.fromkeys(list(total_scores.values())))) == 1:
            next_up = self._create_text_obj("Draw!", pos, Colors.BLACK, 80)
            self.screen.blit(*next_up)
            pygame.display.flip()
            _play_draw_sound()
        else:
            # Show winner
            winners = max(total_scores, key=total_scores.get)
            members = self.teams.teams.get(winners)
            pos = (self.window_width * 0.5, self.window_height * 0.5)

            next_up = self._create_text_obj(f"{winners} The Winners!", pos, get_color_from_name(winners), 80)
            self.screen.blit(*next_up)
            pos = (pos[0], pos[1] + next_up[0].get_height() * 1.5)
            self.screen.blit(
                *self._create_text_obj(', '.join(members), pos, get_color_from_name(winners), 60))

            pygame.display.flip()
            _play_victory_sound(winners, members)

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
        obj = self._create_text_obj(f"Score: {str(self.round_score)}", (x_pos, y_pos), color=Colors.BLUE, size=50)
        self.screen.blit(*obj)

    def _next_up_window(self, team):
        pos = (self.window_width * 0.5, self.window_height * 0.4)
        next_up = self._create_text_obj("Next Up...", pos, Colors.BLACK, 100)
        self.screen.blit(*next_up)
        pos = (pos[0], pos[1] + next_up[0].get_height() * 1.5)
        self.screen.blit(*self._create_text_obj(team, pos, get_color_from_name(team), 90))

    def create_teams(self):
        team_title_text = []
        boxes = {}
        start_x = {}
        for idx, team in enumerate(self.teams.teams.keys()):
            color = get_color_from_name(team)
            width = self.window_width * (0.3625 + idx * 0.425)
            start_x[team] = width
            team_title_text.append(
                self._create_text_obj(team, (width + 70, self.window_height * 0.15), color))
            box = InputBox(width, self.window_height * 0.2, 140, 32)
            boxes[team] = box

        round_box = InputBox(self.window_width * 0.075, self.window_height * 0.15, 64, 32, str(self.number_of_rounds),
                             True, only_int=True)
        round_time_box = InputBox(self.window_width * 0.075, self.window_height * 0.3, 64, 32, str(self.game_time),
                                  only_int=True)

        start_button = Button(self.screen, (self.window_width * 0.575 - 50, self.window_height * 0.9), (100, 50), 15,
                              pygame.Color(*Colors.GRAY), hover_color=pygame.Color(*Colors.LIGHT_GRAY),
                              text="Start Game",
                              cb=partial(self.cb_start_game, round_box.get_text, round_time_box.get_text))

        reset_teams_button = Button(self.screen, (self.window_width * 0.15, self.window_height * 0.9), (100, 50), 15,
                                    pygame.Color(*Colors.GRAY), hover_color=pygame.Color(*Colors.LIGHT_GRAY),
                                    text="Reset Teams", cb=self._cb_reset_teams)

        rounds_title = self._create_text_obj("Rounds", (self.window_width * 0.075, self.window_height * 0.1),
                                             size=40)

        rounds_time_title = self._create_text_obj("Round Time", (self.window_width * 0.075, self.window_height * 0.25),
                                                  size=40)

        categories_title = self._create_text_obj("Categories", (self.window_width * 0.075, self.window_height * 0.4),
                                                 size=40)

        while not self.round_started:
            self._clear_window()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(1)
                start_button.check_click(event)
                reset_teams_button.check_click(event)
                [box.handle_event(event, partial(self.teams.add_team_member, team)) for team, box in boxes.items()]
                [box.handle_event(event) for box in self.categories.group]
                round_box.handle_event(event)
                round_time_box.handle_event(event)
            [box.draw(self.screen) for box in boxes.values()]
            [box.draw(self.screen) for box in self.categories.group]
            round_box.draw(self.screen)
            round_time_box.draw(self.screen)
            [self.screen.blit(*txt_team) for txt_team in team_title_text]

            for team_name, members in self.teams.teams.items():
                text_obj = [
                    self._create_text_obj(f"{idx+1}. {member}",
                                          (start_x.get(team_name), self.window_height * 0.25 + (idx + 1) * 32)) for
                    idx, member in enumerate(members)
                ]

                [self.screen.blit(*obj) for obj in text_obj]
            start_button.draw_button()
            if self.teams.is_members_in_teams():
                reset_teams_button.draw_button()
            pygame.draw.line(self.screen, pygame.Color(*Colors.BLACK),
                             (self.window_width * 0.575, self.window_height * 0.15),
                             (self.window_width * 0.575, self.window_height * 0.85))

            pygame.draw.line(self.screen, pygame.Color(*Colors.BLACK),
                             (self.window_width * 0.15, 0),
                             (self.window_width * 0.15, self.window_height), 2)
            self.screen.blit(*categories_title)
            self.screen.blit(*rounds_title)
            self.screen.blit(*rounds_time_title)
            pygame.display.flip()

    def start_round(self, round_number, team):
        self._clear_window()
        self.round_score.reset_round()
        accept_failure_counter = Counter(ACCEPT_FAIL_TIME, DOWN_COUNT, threshold=0)
        fail_button = Button(self.screen, (self.window_width * 0.35, self.window_height * 0.9), (100, 50), 20,
                             pygame.Color(*Colors.RED), text="Fail",
                             hover_color=pygame.Color(*Colors.LIGHT_RED),
                             cb=partial(self.cb_fail, accept_failure_counter),
                             key_stroke=[pygame.K_LEFT, pygame.K_BACKSPACE, pygame.K_ESCAPE])
        success_button = Button(self.screen, (self.window_width * 0.65, self.window_height * 0.9), (100, 50), 20,
                                pygame.Color(*Colors.GREEN), text="Success",
                                hover_color=pygame.Color(*Colors.LIGHT_GREEN),
                                cb=partial(self.cb_success, accept_failure_counter),
                                key_stroke=[pygame.K_RIGHT, pygame.K_RETURN])

        round_text = self._create_text_obj(f"Round {round_number} | {team}",
                                           (self.window_width * 0.5, self.window_height * 0.1),
                                           color=get_color_from_name(team))

        self.picture_engine.next_picture()

        counter = Counter(self.game_time, DOWN_COUNT, threshold=0)

        while self.round_started:
            buttons = [success_button, fail_button] if self.accept_failure else [success_button]
            if not self.accept_failure:
                try:
                    accept_failure_counter.tick()
                except TimeoutGameOver:
                    self.accept_failure = True
            try:
                counter.tick()
            except TimeoutGameOver:
                # Reset round settings on timeout.
                self.round_started = False
                counter.reset()
                self.teams.score[team].append(self.round_score.score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(1)
                try:
                    [button.check_click(event) for button in buttons]
                except PicturePoolEndedGameOver:
                    self._game_over()
                    self.round_started = False
                    self.picture_engine.reset_used_pictures()
                    self.round_score.reset_round()
                    return
            # Print timer clock
            self._clear_window()
            timer = self.font.render(counter.get_time_string(), True,
                                     Colors.BLACK if counter.time > 10 else Colors.RED)
            height = self.window_height * 0.15
            width = self.window_width * 0.5 - timer.get_size()[0] * 0.5
            obj = self._create_text_obj(counter.get_time_string(), (width, height),
                                        Colors.BLACK if counter.time > 10 else Colors.RED, size=40)
            self.screen.blit(*obj)
            # Drawing buttons
            [button.draw_button() for button in buttons]

            picture_title = self.picture_engine.get_picture_title()
            # Image Title
            self.screen.blit(
                *self._create_text_obj(picture_title, (self.window_width * 0.5, self.window_height * 0.25), size=90))
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

    def _reset_game(self):
        self._clear_window()
        self._score_table()
        self.display_score()
        pygame.time.wait(1000)

    def _cb_reset_teams(self):
        self.teams = Teams(2)

    def start_game(self):
        end_game = False
        self._clear_window()
        pygame.display.set_caption("Anything Goes")

        start_button = Button(self.screen, (self.window_width / 2 - 50, self.window_height * 0.9), (100, 50), 15,
                              pygame.Color(*Colors.GRAY), hover_color=pygame.Color(*Colors.LIGHT_GRAY),
                              text="Start Round", cb=self.cb_start_round)

        self.create_teams()
        selected_categories = self.categories.get_selected()
        self.picture_engine.init_picture_pool(self.path, selected_categories)
        round_counter = 1
        in_round_counter = 0
        teams = list(self.teams.teams.keys())
        self.teams.reset_score()
        countdown: Counter = None
        if not self.picture_engine.has_pictures_left():
            self.picture_engine.reset_used_pictures()
            self.picture_engine.init_picture_pool(self.path, selected_categories)

        while not end_game and self.picture_engine.has_pictures_left():
            self._clear_window()
            self._score_table()
            self._display_round_words()
            self._display_round_score()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(1)
                start_button.check_click(event)

            team = teams[in_round_counter]

            self._next_up_window(team)
            if countdown:
                self.screen.blit(
                    *self._create_text_obj(str(countdown.time), (self.window_width * 0.5, self.window_height * 0.7),
                                           size=200))
                try:
                    countdown.tick()
                except TimeoutGameOver:
                    countdown = None
                    team = teams[in_round_counter]
                    self.start_round(round_counter, team)
                    round_counter = round_counter + in_round_counter
                    in_round_counter = (in_round_counter + 1) % 2
                    self.round_started = False

            if self.round_started:
                if countdown is None:
                    countdown = Counter(3, DOWN_COUNT, threshold=0)
            else:
                start_button.draw_button()

            if round_counter > self.number_of_rounds:
                self._reset_game()
                self.round_score.reset_round()
                end_game = True

            pygame.display.flip()


if __name__ == '__main__':
    user32 = ctypes.windll.user32
    width, height = user32.GetSystemMetrics(16), user32.GetSystemMetrics(17)
    game = Game(width, height, "../pics")
    while True:
        game.start_game()
