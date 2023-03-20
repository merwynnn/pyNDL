import math
from math import sqrt

import numpy as np
import pygame

from NodalLanguage.Colors import colors


class Rope:

    def __init__(self, display):
        self.display = display

        self.input = None
        self.output = None

        self.is_hovered = False
        self.quality = 10
        self.visibility_delta = 40

    def draw(self, pos1=None, pos2=None, pin=None, mouse_pos=(0, 0)):
        # pos1 and pos2 are usefull if you want specific points (when you select a pin for exemple)

        self.is_hovered = False

        if pos1 is not None and pos2 is not None:
            from NodalLanguage.Pin import Input
            if type(pin) is Input:
                pos1_s = pos1
                pos2_s = pos2
            else:
                pos2_s = pos1
                pos1_s = pos2

        else:
            pos1_s = self.input.pos
            pos2_s = self.output.pos

        if pos1_s == (0, 0) or pos2_s == (0, 0):  # Prevent the rope from weirdly bugging sometimes
            return
        if not self.is_on_screen(pos1_s, self.visibility_delta) and not self.is_on_screen(pos2_s, self.visibility_delta):
            return

        dist = math.sqrt((pos1_s[0]-pos2_s[0])**2+(pos1_s[1]-pos2_s[1])**2)
        self.quality = dist/25
        if self.quality < 4:
            self.quality = 4
        if self.quality > 30:
            self.quality = 30
        c_pin = pin if self.input is None else self.input

        dist = math.sqrt((pos1_s[0]-pos2_s[0])**2 + (pos1_s[1]-pos2_s[1])**2)
        m = (pos1_s[0] + pos2_s[0]) / 2, (pos1_s[1] + pos2_s[1]) / 2
        pa_1 = pos1_s[0] - dist / 3, pos1_s[1]
        pa_2 = pos2_s[0] + dist / 3, pos2_s[1]

        color = (255, 255, 255) if c_pin.is_execution_pin else colors[c_pin.type]

        n = self.curve(pos1_s, pa_1, m, color, mouse_pos)
        n1 = self.curve(m, pa_2, pos2_s, color, mouse_pos)
        if n or n1:
            self.is_hovered = True

    def is_on_screen(self, pos, delta):
        if -delta <= pos[0] <= self.display.get_width() + delta and -delta <= pos[
            1] <= self.display.get_height() + delta:
            return True
        return False

    def curve(self, p0, p1, p2, color, mouse_pos=(0, 0)):
        i = False
        lastPoint = None
        for t in np.arange(0, 1, 1/self.quality):
            point = (p0[0] * (1 - t) ** 2 + 2 * (1 - t) * t * p1[0] + p2[0] * t ** 2,
                     p0[1] * (1 - t) ** 2 + 2 * (1 - t) * t * p1[1] + p2[1] * t ** 2)
            if lastPoint is not None:
                pygame.draw.aaline(self.display, color, lastPoint, point, 1)
                if not i:
                    if self.is_rectangle_hovered(lastPoint, point, mouse_pos):
                        i = True
            lastPoint = point
        pygame.draw.aaline(self.display, color, lastPoint, p2, 1)
        return i

    def delete(self):
        del self

    def get_pos_with_delta(self, pos, delta):
        return pos[0] + delta[0], pos[1] + delta[1]

    def is_rectangle_hovered(self, p0, p1, mouse_pos):
        delta = 4
        size = (abs(p0[0]-p1[0]), abs(p0[1]-p1[1]))
        if p0[0] < p1[0]:
            if p0[1] < p1[1]:
                p = p0
            else:
                p = (p0[0], p1[1])
        else:
            if p1[1] < p0[1]:
                p = p1
            else:
                p = (p1[0], p0[1])

        if p[0] <= mouse_pos[0] <= p[0] + size[0] + delta and p[1] <= mouse_pos[1] <= p[1] + \
                size[1] + delta:
            return True

        return False
