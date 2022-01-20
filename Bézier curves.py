from asyncio.proactor_events import _ProactorBasePipeTransport
from random import randint
import pygame as py
from pygame import Rect, gfxdraw
import numpy as np
from math import sqrt, sin, cos
from ctypes import windll
from scipy.special import binom as binomial
from time import sleep

windll.user32.SetProcessDPIAware() # Ignores scaling on the PC
py.display.init()


screen = py.display.set_mode((0, 0), py.FULLSCREEN, py.SRCALPHA)
screen_size = py.display.get_window_size()
print(screen_size)

class Button:
    color = (255, 255, 255)
    radius = 30
    buttons = []

    def __init__(self, pos, color, type):
        self.x, self.y = pos
        self.color = color
        self.shell = black
        self.clicked = False
        self.type = type

        self.buttons.append(self)
    
    def draw(self):
        gfxdraw.filled_circle(screen, self.x, self.y, self.radius, self.color)
        gfxdraw.aacircle(screen, self.x, self.y, self.radius, self.shell)
    
    def collide(self, point):
        if sqrt((self.x - point[0]) ** 2 + (self.y - point[1]) ** 2) < self.radius:
            return True
    
    def updateborder(self, mouse_pos):
        for button in self.buttons:
            if button.collide(mouse_pos):
                button.shell = white
            else:
                if button.clicked:
                    pass
                else:
                    button.shell = black
    
    def click(self):
        mouse_pos = py.mouse.get_pos()
        for button in self.buttons:
            if button.collide(mouse_pos):
                if not button.type and Curve.mode == "Edit":
                    button.clicked = True
                    Button.color = button.color
                    for button_2 in colors:
                        if button_2 != button:
                            button_2.clicked = False
                elif button.type:
                    button.clicked = True
                    for button_2 in modes:
                        if button_2 != button:
                            button_2.clicked = False
                    match button.type:
                        case 1:
                            Curve.mode = "Preview"
                        case 2:
                            Curve.mode = "Edit"


class Animation:
    def __init__(self, curve, radius) -> None:
        
        points = np.array([np.array([self.random_point(point, radius) for point in curve.points]) for i in range(100)])
        for line in points:
            a = curve.B(line).astype(int)
            color = (np.array(curve.color) * np.random.uniform(0.3, 1, 1)).astype(int)
            # self.path = curve.B(points)
            for i, point in enumerate(a[1:]):
                py.draw.line(screen, color, a[i], point, 3)
                "Anti-aliased line: https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line"
        py.display.update()
        sleep(5)
        quit()
    
    def random_point(self, point, radius):
        theta = np.random.uniform(0, 2 * np.pi, 1)
        r = np.random.uniform(0, 1, 1) * radius
        x, y = point[0] + r[0] * cos(theta[0]), point[1] + r[0] * sin(theta[0])
        return [(x, y)]



class Curve:
    n = 500 # Number of lines
    limit = 200 # Everything is perfext with the explisit formula
    mode = "Edit"

    t_values = np.array([np.array((i, i)) for i in np.linspace(0, 1, n)])
    ones = np.array([np.array((i, i)) for i in np.ones(n)])

    border = 20
    rect = Rect(border, border, screen_size[0] - 2 * border, int(screen_size[1] * 0.85))
    
    def __init__(self) -> None:
        self.n = Curve.n
        self.points = []
        self.color = white
        self.clicked = False
        self.thickness = 3
        self.line = []


    @staticmethod
    def extension(arg, t, n, i):
        val = 1
        if i == 0:
            val = 1
        else:
            val = t ** i
        if n == i:
            return val
        else:
            return val * arg ** (n - i)


    def B(self, points):
        # Recursive function for the bézier curve - Wikipedia: https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Recursive_definition
        n = len(points) - 1
        result = sum([binomial(n, i) * self.extension(self.ones - self.t_values, self.t_values, n, i) * points[i] for i in range(0, n + 1)])
        return result


    def bézier(self, mouse):
        points = np.array([np.array(point) for point in self.points + mouse])
        if len(points) > 1:
            self.line = self.B(points).astype(int)
            for i, point in enumerate(self.line[1:]):
                py.draw.line(screen, self.color, self.line[i], point, self.thickness)
                "Anti-aliased line: https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line"
    
    @staticmethod
    def draw_point(pos, r, color):
        x, y = pos
        gfxdraw.filled_circle(screen, x, y, r, color)
        gfxdraw.aacircle(screen, x, y, r, color)
    
    def main(self):
        holding = False

        while True:
            screen.fill(grey)
            for event in py.event.get():
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        quit()
                if event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.rect.collidepoint(py.mouse.get_pos()):
                        if len(self.points) == self.limit:
                            self.points = self.points[:-1]
                        holding = True
                elif event.type == py.MOUSEBUTTONUP:
                    if self.rect.collidepoint(py.mouse.get_pos()):
                        if event.button == 1 and holding:
                            pos = py.mouse.get_pos()
                            if len(self.points) == self.limit:
                                self.points = self.points[:-1].append(pos)
                            else:
                                self.points.append(pos)
                            holding = False
                        elif event.button == 3:
                            self.points = self.points[:-1]
                    else:
                        holding = False
                        Button.click(Button)
            self.color = Button.color
            if not self.rect.collidepoint(py.mouse.get_pos()):
                holding = False
            if self.mode == "Edit":
                self.bézier([py.mouse.get_pos()] if holding else [])
                for point in self.points + [py.mouse.get_pos()] if holding else self.points:
                    self.draw_point(point, 3, white)
            elif self.mode == "Preview":
                line = Animation(self, 25)
            # Buttons
            mouse_pos = py.mouse.get_pos()
            Button.updateborder(Button, mouse_pos)
            for button in Button.buttons:
                button.draw()

            py.draw.rect(screen, black, self.rect, 2, 10)
            

            py.display.update()


black = (0, 0, 0)
dark_grey = (20, 20, 20)
grey = (39, 40, 40)
white_a = (255, 255, 255, 150)
white = (255, 255, 255)
blue = (0, 220, 180)

colors = [Button((int(screen_size[0] / 5 * i), int(screen_size[1] * 0.93)), (50, 40 * i, int(60 / 2 * i)), 0) for i in range(1, 5)]
modes = [Button((screen_size[0] - 50, int(screen_size[1] * 0.93)), black, 1), Button((screen_size[0] - 150, int(screen_size[1] * 0.93)), dark_grey, 2)]
modes[1].clicked = True
modes[1].shell = white

curve = Curve()

if __name__ == '__main__':
    curve.main()


# TODO: Add thickness-slider

# TODO: Add possibility to save and create new lines (Also being able to go back to the previous ones)