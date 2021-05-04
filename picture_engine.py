import os
import random
import pygame


class PictureEngine:
    def __init__(self, path, picture_fixed_size=None):
        self.path = path
        self.pool = self._generate_picture_pool(self.path)
        self.picture_fixed_size = picture_fixed_size
        self.current_picture = None
        self.current_picture_title = None

    @staticmethod
    def _generate_picture_pool(path):
        pics = os.listdir(path)
        random.shuffle(pics)
        return pics

    def draw(self, screen, pos):
        picture = self.get_picture()
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

    def next_picture(self):
        picture = self.pool.pop()
        self.current_picture_title = ''.join(picture.split(".")[:-1])
        self.current_picture = os.path.join(self.path, picture)

    def reset_pool(self):
        self.pool = self._generate_picture_pool(self.path)