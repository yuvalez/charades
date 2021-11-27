import os
import random
import pygame

from game_over_exceptions import PicturePoolEndedGameOver


class PictureEngine:
    def __init__(self, path, picture_fixed_size=None):
        self.path = path
        self.picture_fixed_size = picture_fixed_size
        self.current_picture = None
        self.current_picture_title = None
        self.pool = None
        self.used_pictures = []

    def has_pictures_left(self):
        return len(self.pool) > 0

    def init_picture_pool(self, path, selected_categories=None):
        pics = []
        if selected_categories is None:
            selected_categories = ["הכל"]
        for category in selected_categories:
            pics.extend(list(map(lambda x: os.path.join(category, x), os.listdir(os.path.join(path, category)))))

        # Remove used pictures in this game instance from pool
        [pics.remove(pic) for pic in self.used_pictures]
        random.shuffle(pics)
        self.pool = pics

    def draw(self, screen, pos):
        try:
            picture = self.get_picture()
        except Exception as e:
            self.next_picture()
        if self.picture_fixed_size:
            picture = pygame.transform.scale(picture, self.picture_fixed_size)
        new_width = pos[0] - picture.get_width() // 2
        new_height = pos[1] - picture.get_height() // 2
        screen.blit(picture, (new_width, new_height))

    def get_picture(self):
        try:
            return pygame.image.load(self.current_picture)
        except Exception as e:
            print(self.current_picture)
            print(e)
            raise

    def get_picture_title(self):
        return self.current_picture_title

    def reset_used_pictures(self):
        self.used_pictures = []

    def next_picture(self):
        try:
            picture = self.pool.pop()
        except Exception:
            raise PicturePoolEndedGameOver()
        self.used_pictures.append(picture)
        self.current_picture_title = os.path.basename(''.join(picture.split(".")[:-1]))
        self.current_picture = os.path.join(self.path, picture)