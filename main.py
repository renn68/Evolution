from random import randint
import pyglet
from pyglet.window import key

from settings import Settings
from board import Board
from cell import Cell


uiSet = Settings()
board_batch = pyglet.graphics.Batch()

pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)
pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)
pyglet.gl.glEnable(pyglet.gl.GL_TEXTURE_2D)
pyglet.gl.glTexParameterf(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_NEAREST)
pyglet.gl.glTexParameterf(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MIN_FILTER, pyglet.gl.GL_LINEAR)
pyglet.gl.glEnable(pyglet.gl.GL_COLOR_MATERIAL)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

# Const declarations
MIN_CELLS = 70
MUTATION = 20
BREED_SIZE = 0.85
DEATH_SIZE = 0.5
SEASON_VAR = 1800

config = pyglet.gl.Config(sample_buffers=1, samples=4)


class EvolveWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):

        self.set_location(20, 30)

        super(EvolveWindow, self).__init__(width=uiSet.screenWidth, height=uiSet.screenHeight, resizable=True, *args, **kwargs)

        self.fps_display = pyglet.window.FPSDisplay(self)

        self.cell_tile = pyglet.image.load('resources/cell_60.png')
        # self.cell_tile.anchor_x = 30
        # self.cell_tile.anchor_y = 30
        # self.cell_tile_scale = uiSet.cell_scale
        self.cell_tile_center = pyglet.image.load('resources/cell_60_center.png')
        # self.cell_tile_center.anchor_x = 30
        # self.cell_tile_center.anchor_y = 30
        # self.cell_tile_center_scale = uiSet.cell_scale / 2

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

        self.breed_count = 0
        self.death_count = 0

        self.last_month = 1

        self.elder = 0

        self.generation = 0

        self.attack = 0

        self.season_chance = SEASON_VAR

    def on_key_press(symbol, modifier):
        if symbol == key.ESCAPE:
            print('escape')
            pass
        pass

    def stats(self):
        self.cell_count_label = pyglet.text.Label("Current Cells: " + str(len(cells)), font_name='Veranda',
                                                  font_size=12, color=(204, 153, 255, 255), x=148, y=1005,
                                                  batch=board_batch, bold=True)
        self.breed_count_label = pyglet.text.Label("Children: " + str(self.breed_count), font_name='Veranda',
                                                   font_size=12, color=(204, 204, 102, 255), x=304, y=1005,
                                                   batch=board_batch, bold=True)
        self.death_count_label = pyglet.text.Label("Dead cells: " + str(self.death_count), font_name='Veranda',
                                                   font_size=12, color=(51, 153, 255, 255), x=444, y=1005,
                                                   batch=board_batch, bold=True)
        self.elder_label = pyglet.text.Label("Oldest cell: " + str(self.elder), font_name='Veranda',
                                             font_size=12, color=(255, 0, 255, 255), x=604, y=1005,
                                             batch=board_batch, bold=True)
        self.generation_label = pyglet.text.Label("Highest Gen: " + str(self.generation), font_name='Veranda',
                                                  font_size=12, color=(0, 204, 155, 255), x=736, y=1005,
                                                  batch=board_batch, bold=True)
        self.attacks_label = pyglet.text.Label("Attacks: " + str(self.attack), font_name='Veranda',
                                               font_size=12, color=(255, 0, 0, 255), x=888, y=1005,
                                               batch=board_batch, bold=True)

    def stats_update(self):
        self.cell_count_label.text = ("Current Cells: %4d" % (len(cells)))
        children_text = float(self.breed_count / 1000)
        self.breed_count_label.text = ("Children: %5.2fk" % (children_text))

    def season_check(self):
        if self.last_month != board.date.month:
            board.grow()
            self.last_month = board.date.month
            _ice = randint(1, self.season_chance)
            if _ice == 1:
                board.ice_age(-0.3)
                print('Ice Age')
                self.season_chance = SEASON_VAR
            elif _ice == 2:
                board.ice_age(0.3)
                print('Bountiful Season')
                self.season_chance = SEASON_VAR
            else:
                self.season_chance -= 1

    def on_draw(self):
        self.clear()

        # pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        # pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)
        # pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)
        # pyglet.gl.glEnable(pyglet.gl.GL_TEXTURE_2D)
        # pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_NEAREST)
        # pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MIN_FILTER, pyglet.gl.GL_LINEAR)
        # pyglet.gl.glEnable(pyglet.gl.GL_COLOR_MATERIAL)
        # pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        # pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

        board_batch.draw()
        self.fps_display.draw()

    def update(self, dt):
        i = 0
        cells_length = len(cells)
        while i < cells_length:
            if cells[i].health['cell_size'] > DEATH_SIZE:
                cells[i].action()
                i += 1
            else:
                cells[i].cell_image.__del__()
                cells[i].cell_image_center.__del__()
                cells[i].alive = False
                board.update_tile(cells[i].loc['x_loc'], cells[i].loc['y_loc'], 20)
                self.death_count += 1
                death_text = float(self.death_count / 1000)
                self.death_count_label.text = "Dead cells: %6.2fk" % (death_text)

                if cells[i].children > 0:
                    cells_dead.append(cells.pop(i))
                else:
                    del cells[i]
                cells_length -= 1

        board.day_pass()

        if len(cells) < MIN_CELLS:
            cells.append(Cell(uiSet, board_batch, board, self.cell_tile, self.cell_tile_center))
        if randint(1, 1000) == 1:
            for _ in range(30):
                cells.append(Cell(uiSet, board_batch, board, self.cell_tile, self.cell_tile_center))

        self.cell_check()
        self.stats_update()
        self.season_check()

    def cell_check(self):
        self.elder = 0
        self.generation = 0
        for b in range((len(cells))):
            _seen = 0
            for a in range(len(cells)):

                if (cells[b].loc['x_loc'] == cells[a].loc['x_loc']) and (cells[b].loc['y_loc'] == cells[a].loc['y_loc']):
                    _seen = 1

                    if (cells[b].feelings['horny'] > 0.0 and cells[b].health['cell_size'] > BREED_SIZE) and (cells[a].health['cell_size'] > BREED_SIZE):

                        self.breed_count += 1
                        cells.append(Cell(uiSet, board_batch, board, self.cell_tile, self.cell_tile_center, mother=cells[b], father=cells[a]))
                        cells[a].breed()
                        cells[b].breed()

                    if (cells[b].feelings['aggression'] > 0.5):
                        cells[b].attack()
                        cells[a].injured(cells[b].stats['damage'])
                        self.attack += 1

                    cells[b].eyes['neighbour_h'] = (cells[a].stats['race'] / 360)
                    cells[b].eyes['neighbour_s'] = cells[a].health['cell_size']

            _year = board.date.year - cells[b].birthday.year
            if self.elder < _year:
                self.elder = _year
            if self.generation < cells[b].generation:
                self.generation = cells[b].generation

            if _seen == 0:
                cells[b].eyes['neighbour_h'] = 0
                cells[b].eyes['neighbour_s'] = 0

        self.elder_label.text = "Oldest cell: %4d" % (self.elder)
        self.generation_label.text = "Highest Gen: %4d" % (self.generation)
        attack_text = float(self.attack / 1000)
        self.attacks_label.text = "Attack: %6.2fk" % (attack_text)


if __name__ == '__main__':

    evolve_window = EvolveWindow(config=config)

    board = Board(uiSet, board_batch)
    cells = []
    cells_dead = []
    for a in range(MIN_CELLS):
        cells.append(Cell(uiSet, board_batch, board, evolve_window.cell_tile, evolve_window.cell_tile_center))

    evolve_window.stats()
    pyglet.app.run()
