import pyglet
import datetime

# import random
import util
# import colorsys


class Board():

    def __init__(self, uiSet, board_batch):

        self.uiSet = uiSet
        self.board_batch = board_batch

        self.color_v = 1

        self.date = datetime.date(1, 1, 1)

        self.background = pyglet.graphics.OrderedGroup(0)
        self.midground = pyglet.graphics.OrderedGroup(1)
        self.board = []
        self.label_food = []
        # self.label_foodmax = []
        self.board_tile = []

        self.grass_tile = pyglet.image.load('resources/grass_tile_50_2.png')

        self.generate()

    def generate(self):
        food_map = util.HillGrid(ITER=300, _y=self.uiSet.cellHigh, _x=self.uiSet.cellWide)
        food_map_max = util.get_max(food_map.grid)
        fertility_map = util.HillGrid(ITER=400, _y=self.uiSet.cellHigh, _x=self.uiSet.cellWide)
        fertility_map_max = util.get_max(fertility_map.grid)
        water_map = util.water(self.uiSet.cellHigh, self.uiSet.cellWide, 12)

        for y in range(self.uiSet.cellHigh):
            self.board.append([])
            for x in range(self.uiSet.cellWide):
                if water_map[y][x] == 0:
                    color_s = 1
                    color_h = 237.6 / 360
                else:
                    color_s = fertility_map.grid[y][x] / fertility_map_max
                    color_h = food_map.grid[y][x] / food_map_max * 150 / 360

                self.board[y].append([color_s, color_s, color_h])
        self.draw()

    def day_pass(self):
        self.date += datetime.timedelta(days=1)
        self.date_label.text = ("Date: " + str(self.date.__str__()))

    def grow(self):
        for y in range(self.uiSet.cellHigh):
            for x in range(self.uiSet.cellWide):
                if self.board[y][x][1] < 1:
                    self.board[y][x][1] += (self.board[y][x][0] / 90)
                    if self.board[y][x][1] > 1:
                        self.board[y][x][1] = 1

                self.board_tile[y][x].color = util.hsv2rgb(self.board[y][x][2], self.board[y][x][1], self.color_v)
                # self.label_food[y][x].text = (str(round(self.board[y][x][1] * 100)))

    def ice_age(self, action):
        for y in range(self.uiSet.cellHigh):
            for x in range(self.uiSet.cellWide):
                if self.board[y][x][2] < 0.5:
                    self.board[y][x][1] += action
                    if self.board[y][x][1] > 1:
                        self.board[y][x][1] = 1
                    if self.board[y][x][1] < 0.01:
                        self.board[y][x][1] = 0.01

                self.board_tile[y][x].color = util.hsv2rgb(self.board[y][x][2], self.board[y][x][1], self.color_v)

    def draw(self):

        self.date_label = pyglet.text.Label("Date: " + str(self.date.__str__()), font_name='Veranda',
                                            font_size=12, color=(255, 255, 255, 255), x=5, y=1005,
                                            batch=self.board_batch, group=self.midground, bold=True)

        for y in range(self.uiSet.cellHigh):
            # self.label_food.append([])
            # self.label_foodmax.append([])
            self.board_tile.append([])
            for x in range(self.uiSet.cellWide):

                self.board_tile[y].append(pyglet.sprite.Sprite(self.grass_tile,
                                                               x=(x * self.uiSet.cellWidth), y=(y * self.uiSet.cellHeight), batch=self.board_batch,
                                                               group=self.background,))
                self.board_tile[y][x].scale = self.uiSet.scale

                self.board_tile[y][x].color = util.hsv2rgb(self.board[y][x][2], self.board[y][x][1], self.color_v)

                # self.label_food[y].append(pyglet.text.Label(str(round(self.board[y][x][1] * 100)),
                #                                             font_name='Veranda',
                #                                             font_size=6,
                #                                             color=(255, 255, 255, 255),
                #                                             x=((x * self.uiSet.cellWidth) + (self.uiSet.cellWidth // 4)),
                #                                             y=((y * self.uiSet.cellHeight) + (self.uiSet.cellHeight // 1.25)),
                #                                             anchor_x='center',
                #                                             anchor_y='center',
                #                                             batch=self.board_batch,
                #                                             group=self.midground,
                #                                             bold=True))
                #
                # self.label_foodmax[col].append(pyglet.text.Label(str(round(self.board[col][row][0]*100)),
                #                                                  font_name='Veranda',
                #                                                  font_size=8,
                #                                                  color=(255, 255, 255, 255),
                #                                                  x=((row*self.uiSet.cellWidth)+(self.uiSet.cellWidth//1.25)),
                #                                                  y=((col*self.uiSet.cellHeight)+(self.uiSet.cellHeight//1.25)),
                #                                                  anchor_x='center',
                #                                                  anchor_y='center',
                #                                                  batch=self.board_batch,
                #                                                  group=self.midground,
                #                                                  bold=True))

    def update_tile(self, x, y, m):
        self.board[y][x][1] += (m / 100)
        if self.board[y][x][1] < 0.01:
            self.board[y][x][1] = 0.01
        if self.board[y][x][1] > 1:
            self.board[y][x][1] = 1
        self.board_tile[y][x].color = util.hsv2rgb(
            self.board[y][x][2], self.board[y][x][1], self.color_v)
        # self.label_food[y][x].text = (str(round(self.board[y][x][1] * 100)))
