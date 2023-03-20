import pygame
import os

path = os.path.dirname(__file__) + "\Assets\\"

images = {"cross": pygame.image.load(path + "Images\Cross.png"),
          "go_back_arrow": pygame.image.load(path + "Images\GoBackArrow.png")}


def init():
    global images
    for image in images.values():
        image.convert_alpha()
