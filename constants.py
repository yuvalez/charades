import random
import re

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    LIGHT_RED = (255, 100, 100)
    GREEN = (0, 255, 0)
    LIGHT_GREEN = (100, 255, 100)
    GRAY = (155, 155, 155)
    LIGHT_GRAY = (200, 200, 200)
    PINK = (255,192,203)
    BLUE = (0,0,203)
    BROWN = (165,42,42)
    YELLOW = (153,153,0)
    ORANGE = (255,69,0)

UP_COUNT = True
DOWN_COUNT = False

# In seconds
GAME_TIME = 10
FRAME_RATE = 60
# 3 for each team
NUMBER_OF_ROUNDS = 1

GAME_FONT = "Adobe Hebrew Regular.otf"


def name_generator():
    color_options = ["Red", "Pink", "Orange", "Yellow", "Blue", "Brown", "Green"]
    name_options = ["Indian", "Panthers", "Warriors", "Oranges", "Tomatoes", "Foxes", "Socks", "Pills", "Frisbee"]

    color = random.choice(color_options)
    name = random.choice(name_options)

    return color + name

def get_color_from_name(name):
    color = re.findall('[A-Z][^A-Z]*', name)[0]
    return Colors.__getattribute__(Colors(), color.upper())