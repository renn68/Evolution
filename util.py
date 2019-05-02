import colorsys
import random
import math
from noise import pnoise2


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def create_quad_vertex(x, y, width, height):
    return x, y, x + width, y, x + width, y + height, x, y + height


def create_quad_color(a, b, c):
    return a, b, c, a, b, c, a, b, c, a, b, c


def get_max(my_list):
    m = None
    for item in my_list:
        if isinstance(item, list):
            item = get_max(item)
        if not m or m < item:
            m = item
    return m


def water(_y, _x, _noise=12):
    random.seed()
    octaves = random.random()
    octaves = 0.9
    octaves = (random.random() * 0.5) + 0.5
    freq = _noise * octaves
    a = []
    for y in range(_y):
        a.append([])
        for x in range(_x):
            n = int(pnoise2(x / freq, y / freq, 1) * 10 + 3)
            if n >= 1:
                n = 1
            else:
                n = 0
            a[y].append(n)
    return a


class HillGrid:

    def __init__(self, KRADIUS=(1.0 / 5.0), ITER=200, _y=40, _x=40):
        self.KRADIUS = KRADIUS
        self.ITER = ITER
        self._y = _y
        self._x = _x

        self.grid = [[0 for x in range(self._y)] for y in range(self._x)]

        self.MAX = self._y * self.KRADIUS
        for i in range(self.ITER):
            self.step()

    def dump(self):
        for ele in self.grid:
            s = ''
            for alo in ele:
                s += '%s ' % str(alo)
            print(s)

    def __getitem__(self, n):
        return self.grid[n]

    def step(self):
        point = [random.randint(0, self._y - 1), random.randint(0, self._x - 1)]
        radius = random.uniform(0, self.MAX)

        x2 = point[0]
        y2 = point[1]

        for x in range(self._y):
            for y in range(self._x):

                z = (radius**2) - (math.pow(x2 - x, 2) + math.pow(y2 - y, 2))
                if z >= 0:
                    self.grid[x][y] += int(z)
