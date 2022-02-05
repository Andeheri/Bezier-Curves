from asyncio.proactor_events import _ProactorBasePipeTransport
from random import randint
import pygame as py
from pygame import Rect, gfxdraw
import numpy as np
from math import sqrt, sin, cos
from ctypes import windll
from scipy.special import binom as binomial
import time

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
    
    def click(self, a):
        global change
        mouse_pos = py.mouse.get_pos()
        for button in self.buttons:
            if button.collide(mouse_pos):
                if not button.type and Curve.mode == "Edit":
                    button.clicked = True
                    Button.color = button.color
                    a.color = button.color
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
                            if Curve.mode != "Edit":
                                Curve.lines = None
                            Curve.mode = "Edit"


class Animation:
    interval = 0.15
    n = 100
    def __init__(self, curve, radius) -> None:
        self.time = time.time()
        self.curve = curve
        self.radius = radius
        self.lines = [np.array([curve.points[0]] + [self.random_point(point, radius) for point in curve.points[1:-1]] + [curve.points[-1]]) for i in range(self.n)]
        self.paths = [curve.B(line).astype(int) for line in self.lines]
        # With random start- and end-points: line = np.array([self.random_point(point, radius) for point in curve.points])
        # line = np.array([curve.points[0]] + [self.random_point(point, radius) for point in curve.points[1:-1]] + [curve.points[-1]])
        self.particles = [Particle(self.paths[randint(0, self.n - 1)], (np.array(curve.color) * np.random.uniform(0.3, 1, 1)).astype(int), self, 0)]

    def random_point(self, point, radius):
        theta = np.random.uniform(0, 2 * np.pi, 1)
        r = np.random.uniform(0, 1, 1) * radius
        x, y = point[0] + r[0] * cos(theta[0]), point[1] + r[0] * sin(theta[0])
        return [(x, y)]
    
    def draw(self):
        for particle in self.particles:
            particle.update_pos()
        if time.time() - self.time > self.interval:
            self.time = time.time()
            for i in range(randint(4,7)):
                # With random start- and end-points: line = np.array([self.random_point(point, self.radius) for point in curve.points])
                # line = np.array([self.curve.points[0]] + [self.random_point(point, self.radius) for point in self.curve.points[1:-1]] + [self.curve.points[-1]])
                self.particles.append(Particle(self.paths[randint(0, self.n - 1)], (np.array(self.curve.color) * np.random.uniform(0.3, 1, 1)).astype(int), self, len(self.particles)))


class Particle():
    base = 25
    base_speed = 1
    def __init__(self, path, color, parent, index) -> None:
        self.parent_index = index
        self.parent = parent
        self.path = path
        self.points = [path[0], path[1]]
        self.index = 1
        self.color = color
        self.speed = np.random.uniform(1, self.parent.curve.n / 300 * 2) * self.base_speed
        self.trail_lenght = self.base / self.speed
    
    def update_pos(self):
        self.index += self.speed
        var = int(self.index)
        for i, point in enumerate(self.points[1:]):
            py.draw.line(screen, self.color, self.points[i], point, 1)
        if var - 1 < len(self.path) - 1:
            self.points.append(self.path[var])
        if len(self.points) > self.trail_lenght or var > len(self.path):
            self.points = self.points[int(self.speed):]
        if not len(self.points):
            self.parent.particles.pop(self.parent.particles.index(self))


class Curve:
    n = 150 # Number of lines per curve
    limit = 200 # Everything is perfext with the explisit formula
    mode = "Edit"
    curves = []
    lines = None
    elapsed_time = 0
    fps = 1 / 120
    update = True

    t_values = np.array([np.array((i, i)) for i in np.linspace(0, 1, n)])
    ones = np.array([np.array((i, i)) for i in np.ones(n)])

    border = 20
    rect = Rect(border, border, screen_size[0] - 2 * border, int(screen_size[1] * 0.85))
    
    def __init__(self):
        self.n = Curve.n
        self.points = []
        self.color = white
        self.clicked = False
        self.thickness = 3
        self.line = []
        self.curves.append(self)


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
                if event.type == py.KEYUP:
                    if event.key == py.K_RIGHT and self.mode == "Edit" and len(self.points):
                        # Creates a new curve or goes to the next one
                        if (i := self.curves.index(self)) == len(self.curves) - 1:
                            curve_2 = Curve()
                            curve_2.color = Button.color
                            curve_2.main()
                        else:
                            self.curves[i + 1].main()
                    elif event.key == py.K_LEFT and self.mode == "Edit":
                        # Goes to the previous curve
                        if not (i := self.curves.index(self)) == 0:
                            self.curves[i - 1].main()
                    elif event.key == py.K_DELETE:
                        # Clears out points
                        self.points = []
                if event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.rect.collidepoint(py.mouse.get_pos()):
                        if len(self.points) == self.limit:
                            self.points = self.points[:-1]
                        holding = True
                elif event.type == py.MOUSEBUTTONUP:
                    if self.rect.collidepoint(py.mouse.get_pos()) and self.mode == "Edit":
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
                        Button.click(Button, self)
            
            if not self.rect.collidepoint(py.mouse.get_pos()):
                holding = False
            if self.mode == "Edit":
                self.lines = None
                for line in self.curves:
                    if len(line.points):
                        if line == self:
                            self.bézier([py.mouse.get_pos()] if holding else [])
                        else:
                            line.bézier([])
                for point in self.points + [py.mouse.get_pos()] if holding else self.points:
                    self.draw_point(point, 3, white)
            elif self.mode == "Preview":
                if self.lines == None:
                    if len(self.curves[-1].points) > 1:
                        self.lines = [Animation(curve, 25) for curve in self.curves]
                    else:
                        self.lines = [Animation(curve, 25) for curve in self.curves[:-1]] if len(self.curves) else []
                if time.time() - self.elapsed_time > self.fps:
                    self.elapsed_time = time.time()
                    for line in self.lines:
                        line.draw()
                    self.update = True
            # Buttons
            mouse_pos = py.mouse.get_pos()
            Button.updateborder(Button, mouse_pos)
            for button in Button.buttons:
                button.draw()

            py.draw.rect(screen, black, self.rect, 2, 10)
            if self.mode == "Edit":
                py.display.update()
            elif self.mode == "Preview" and self.update:
                py.display.update()
                self.update = False


black = (0, 0, 0)
dark_grey = (20, 20, 20)
grey = (39, 40, 40)
white_a = (255, 255, 255, 150)
white = (255, 255, 255)
blue = np.array((0, 44, 36))
red = np.array((50, 5, 2))

colors = [Button((int(screen_size[0] / 5 * i), int(screen_size[1] * 0.93)), (blue * i).astype(int), 0) for i in range(1, 5)]
modes = [Button((screen_size[0] - 50, int(screen_size[1] * 0.93)), black, 1), Button((screen_size[0] - 150, int(screen_size[1] * 0.93)), dark_grey, 2)]
modes[1].clicked = True
modes[1].shell = white

curve = Curve()

if __name__ == '__main__':
    curve.main()


# TODO: Add thickness-slider

# TODO: Add possibility to save and create new lines (Also being able to go back to the previous ones)