import pyglet

from math import sin, cos, radians
from random import randint
import random
import scipy.special
import numpy as np

import util

MUTATION_LEVEL = 800
MUTATION_CHANCE = 40


class Cell():

    def __init__(self, uiSet, main_batch, board, cell_tile, cell_tile_center, mother=None, father=None):

        self.board = board
        self.uiSet = uiSet
        self.mother = mother
        self.father = father

        self.loc = {'x': (self.uiSet.cellWidth * (1 + randint(1, (uiSet.cellWide - 2)))), 'y': (self.uiSet.cellHeight * (1 + randint(1, (uiSet.cellWide - 2)))),
                    'cell_rotation': randint(0, 360), 'cell_rotation_vel': 0, 'cell_velocity': 0}
        self.loc.update({'x_loc': int(self.loc['x'] / self.uiSet.cellWidth), 'y_loc': int(self.loc['y'] / self.uiSet.cellHeight)})

        self.stats = {'fitness': 1, 'defence': 1, 'damage': 1, 'max_size': 1, 'race': (randint(20, 340)), 'growth': 1, 'food_pref': randint(1, 150)}

        self.eyes = {'eye_l_h': 0, 'eye_l_s': 0, 'eye_c_h': 0, 'eye_c_s': 0, 'eye_r_h': 0, 'eye_r_s': 0, 'neighbour_h': 0, 'neighbour_s': 0}

        self.feelings = {'aggression': 0, 'horny': 0, 'hunger': 0}

        self.health = {'cell_size': 0.75, 'injured': 0, 'health': 0, 'regen': 1}
        self.health['health'] = int(self.health['cell_size'] * 100)

        self.brain = {'inodes': None, 'hnodes': None, 'onodes': None, 'wih': None, 'wio': None, 'memory': [0, 0, 0, 0], 'const': 1}

        self.generation = 0

        self.children = 0

        self.alive = True

        self.birthday = self.board.date

        if self.mother is not None:
            if self.father is not None:
                self.birth()

                # graphics prep
        self.main_batch = main_batch
        self.front = pyglet.graphics.OrderedGroup(2)
        self.front_center = pyglet.graphics.OrderedGroup(3)

        self.cell_tile = cell_tile
        self.cell_tile.anchor_x = 30
        self.cell_tile.anchor_y = 30
        self.cell_tile_scale = self.uiSet.cell_scale
        self.cell_tile_center = cell_tile_center
        self.cell_tile_center.anchor_x = 30
        self.cell_tile_center.anchor_y = 30
        self.cell_tile_center_scale = self.uiSet.cell_scale / 2

        self.draw()
        self.see()
        self.build_brain()

    def action(self):
        self.see()
        self.think()
        self.eat()
        self.rotation()
        self.move()
        _yr = self.board.date.year - self.birthday.year
        if _yr > 30:
            self.health['cell_size'] /= 1 + (0.0001 * (_yr / 30))

    def rotation(self):
        self.loc['cell_rotation'] += self.loc['cell_rotation_vel']
        self.cell_image.rotation = self.loc['cell_rotation']
        self.health['cell_size'] /= 1 + (0.001 * abs(self.loc['cell_rotation_vel']))

    def move(self):
        self.loc['cell_velocity'] /= 2
        if self.loc['x'] + (self.loc['cell_velocity'] * sin(radians(self.loc['cell_rotation']))) < (0 + (self.health['cell_size'] * 60 * self.cell_tile_scale)):
            self.loc['cell_rotation'] = 90
            self.loc['cell_velocity'] = 0.1
            self.health['cell_size'] /= 1.005
        if self.loc['x'] + (self.loc['cell_velocity'] * sin(radians(self.loc['cell_rotation']))) > ((self.uiSet.cellWide * self.uiSet.cellWidth) - (self.health['cell_size'] * 60 * self.cell_tile_scale)):
            self.loc['cell_rotation'] = 270
            self.loc['cell_velocity'] = 0.1
            self.health['cell_size'] /= 1.005
        if self.loc['y'] + (self.loc['cell_velocity'] * cos(radians(self.loc['cell_rotation']))) < (0 + (self.health['cell_size'] * 60 * self.cell_tile_scale)):
            self.loc['cell_rotation'] = 0
            self.loc['cell_velocity'] = 0.1
            self.health['cell_size'] /= 1.005
        if self.loc['y'] + (self.loc['cell_velocity'] * cos(radians(self.loc['cell_rotation']))) > ((self.uiSet.cellHigh * self.uiSet.cellHeight) - (self.health['cell_size'] * 60 * self.cell_tile_scale)):
            self.loc['cell_rotation'] = 180
            self.loc['cell_velocity'] = 0.1
            self.health['cell_size'] /= 1.005

        self.loc['x'] = self.loc['x'] + (self.loc['cell_velocity'] * sin(radians(self.loc['cell_rotation'])))
        self.loc['y'] = self.loc['y'] + (self.loc['cell_velocity'] * cos(radians(self.loc['cell_rotation'])))

        self.cell_image.update(x=self.loc['x'], y=self.loc['y'])
        self.cell_image_center.update(x=self.loc['x'], y=self.loc['y'])

        self.health['cell_size'] /= 1 + ((6 + (0.7 * abs(self.loc['cell_velocity'])) + (5 * (self.health['cell_size'] - self.stats['max_size']))) * 0.0001)
        self.cell_image.scale = (self.health['cell_size']) * self.cell_tile_scale

        self.loc['x_loc'] = int(self.loc['x'] / self.uiSet.cellWidth)
        self.loc['y_loc'] = int(self.loc['y'] / self.uiSet.cellHeight)

    def eat(self):
        if self.health['injured'] > 0:
            self.health['injured'] -= 0.05
        if self.board.board[self.loc['y_loc']][self.loc['x_loc']][2] > 0.5:
            self.health['cell_size'] /= 1 + (0.001 * (0.5 / self.health['cell_size']))
        else:
            if self.board.board[self.loc['y_loc']][self.loc['x_loc']][1] > 0.01:
                if self.feelings['hunger'] > 0:
                    change = 1 + (0.0018 - (abs(self.board.board[self.loc['y_loc']][self.loc['x_loc']][2] - (self.stats['food_pref'] / 360)) / 135))
                    if change > 1:
                        change = 1 + ((change - 1) * (self.stats['max_size'] / pow((self.health['cell_size'] + 0.25), 2)))
                    self.health['cell_size'] *= change

                    self.cell_image.scale = (self.health['cell_size']) * self.cell_tile_scale
                    self.board.update_tile(self.loc['x_loc'], self.loc['y_loc'], -0.1)
        if self.health['cell_size'] > 4:
            self.health['cell_size'] = 3

    def draw(self):
        self.cell_image = pyglet.sprite.Sprite(self.cell_tile, x=self.loc['x'], y=self.loc['y'], batch=self.main_batch, group=self.front, subpixel=True)
        self.cell_image_center = pyglet.sprite.Sprite(self.cell_tile_center, x=self.loc['x'], y=self.loc['y'], batch=self.main_batch, group=self.front_center, subpixel=True)

        self.cell_image.scale = (self.health['cell_size']) * self.cell_tile_scale
        self.cell_image.rotation = self.loc['cell_rotation']
        self.cell_image.color = util.hsv2rgb((self.stats['race'] / 360), 0.8, 0.9)

        self.cell_image_center.scale = self.cell_tile_center_scale
        self.cell_image_center.color = util.hsv2rgb((self.stats['food_pref'] / 360), 0.8, 0.9)

    def see(self):
        x = self.loc['x_loc']
        y = self.loc['y_loc']
        self.eyes['eye_c_s'] = self.board.board[y][x][1]
        self.eyes['eye_c_h'] = (self.board.board[y][x][0]) * (360 / 150)

        left_eye = self.loc['cell_rotation'] - 30
        right_eye = self.loc['cell_rotation'] + 30
        eye_length = 2 * self.health['cell_size'] * 60 * self.cell_tile_scale

        x = self.loc['x'] - (eye_length * sin(radians(left_eye)))
        x = int(x / self.uiSet.cellWidth)
        if x > (self.uiSet.cellHigh - 1):
            x = self.loc['x_loc']
        y = self.loc['y'] + (eye_length * cos(radians(left_eye)))
        y = int(y / self.uiSet.cellWidth)
        if y > (self.uiSet.cellWide - 1):
            y = self.loc['y_loc']

        self.eyes['eye_l_s'] = self.board.board[y][x][1]
        self.eyes['eye_l_h'] = self.board.board[y][x][0] * (360 / 150)

        x = self.loc['x'] + (eye_length * sin(radians(right_eye)))
        x = int(x / self.uiSet.cellWidth)
        if x > (self.uiSet.cellHigh - 1):
            x = self.loc['x_loc']
        y = self.loc['y'] + (eye_length * cos(radians(right_eye)))
        y = int(y / self.uiSet.cellWidth)
        if y > (self.uiSet.cellWide - 1):
            y = self.loc['y_loc']

        self.eyes['eye_r_s'] = self.board.board[y][x][1]
        self.eyes['eye_r_h'] = self.board.board[y][x][0] * (360 / 150)

    def activation_function(self, xx):
        return scipy.special.expit(xx)

    def build_brain(self):

        self.brain['inodes'] = [self.eyes['eye_l_h'], self.eyes['eye_l_s'], self.eyes['eye_c_h'], self.eyes['eye_c_s'], self.eyes['eye_r_h'], self.eyes['eye_r_s'], self.eyes['neighbour_h'], self.eyes['neighbour_s'],
                                self.health['cell_size'], self.health['injured'], self.brain['memory'][0], self.brain['memory'][1], self.brain['const']]
        self.brain['hnodes'] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, self.brain['const']]
        self.brain['onodes'] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, self.brain['const']]
        if self.brain['wih'] is None:
            self.brain['wih'] = np.random.normal(0.0, pow(len(self.brain['inodes']), -0.4), (len(self.brain['hnodes']), len(self.brain['inodes'])))
        if self.brain['wio'] is None:
            self.brain['wio'] = np.random.normal(0.0, pow(len(self.brain['hnodes']), -0.4), (len(self.brain['onodes']), len(self.brain['hnodes'])))

    def think(self):

        self.brain['inodes'] = [self.eyes['eye_l_h'], self.eyes['eye_l_s'], self.eyes['eye_c_h'], self.eyes['eye_c_s'], self.eyes['eye_r_h'], self.eyes['eye_r_s'], self.eyes['neighbour_h'], self.eyes['neighbour_s'],
                                self.health['cell_size'], self.health['injured'], self.brain['memory'][0], self.brain['memory'][1], self.brain['const']]

        # convert inputs list to 2d array
        inputs = np.array(self.brain['inodes'], ndmin=2).T

        # calculate signals into hidden layer
        hidden_inputs = np.dot(self.brain['wih'], inputs)
        # calculate the signals emerging from hidden layer
        hidden_outputs = self.activation_function(hidden_inputs)
        hidden_outputs[-1] = self.brain['const']

        # calculate signals into output layer
        final_inputs = np.dot(self.brain['wio'], hidden_outputs)
        # calculate the sigmoid from the output layer
        final_outputs = final_inputs  # self.activation_function(final_inputs)
        final_outputs[-1] = self.brain['const']

        self.loc['cell_rotation_vel'] = (final_outputs[0])
        self.loc['cell_velocity'] = (final_outputs[1])
        self.feelings['hunger'] = final_outputs[2]
        self.feelings['horny'] = final_outputs[3]
        self.feelings['aggression'] = final_outputs[4]
        self.brain['memory'][0] = final_outputs[-3]
        self.brain['memory'][1] = final_outputs[-2]

    def breed(self):
        self.health['cell_size'] *= 0.65
        self.children += 1
        pass

    def birth(self):
        self.loc['x'] = ((self.mother.loc['x'] + self.father.loc['x']) / 2)
        self.loc['y'] = ((self.mother.loc['y'] + self.father.loc['y']) / 2)
        self.loc.update({'x_loc': int(self.loc['x'] / self.uiSet.cellWidth), 'y_loc': int(self.loc['y'] / self.uiSet.cellHeight)})
        _wih = np.random.normal(0.5, (1 / MUTATION_LEVEL), (len(self.mother.brain['hnodes']), len(self.father.brain['inodes'])))
        _wio = np.random.normal(0.5, (1 / MUTATION_LEVEL), (len(self.mother.brain['onodes']), len(self.father.brain['hnodes'])))
        self.brain['wih'] = np.multiply(np.add(self.mother.brain['wih'], self.father.brain['wih']), _wih)
        self.brain['wio'] = np.multiply(np.add(self.mother.brain['wio'], self.father.brain['wio']), _wio)

        self.stats['fitness'] = (self.mother.stats['fitness'] + self.father.stats['fitness']) / 2
        if randint(1, MUTATION_CHANCE) == 1:
            self.stats['fitness'] += random.uniform(-0.1, 0.1)
        self.stats['defence'] = (self.mother.stats['defence'] + self.father.stats['defence']) / 2
        if randint(1, MUTATION_CHANCE) == 1:
            self.stats['defence'] += random.uniform(-0.1, 0.1)
        self.stats['damage'] = (self.mother.stats['damage'] + self.father.stats['damage']) / 2
        if randint(1, MUTATION_CHANCE) == 1:
            self.stats['damage'] += random.uniform(-0.1, 0.1)
        self.stats['max_size'] = (self.mother.stats['max_size'] + self.father.stats['max_size']) / 2
        if randint(1, MUTATION_CHANCE) == 1:
            self.stats['max_size'] += random.uniform(-0.1, 0.1)
        self.stats['race'] = (self.mother.stats['race'] + self.father.stats['race']) / 2
        if randint(1, MUTATION_CHANCE) == 1:
            self.stats['race'] += random.uniform(-3, 3)
        self.stats['growth'] = (self.mother.stats['growth'] + self.father.stats['growth']) / 2
        if randint(1, MUTATION_CHANCE) == 1:
            self.stats['growth'] += random.uniform(-3, 3)
        self.stats['food_pref'] = (self.mother.stats['food_pref'] + self.father.stats['food_pref']) / 2
        if randint(1, MUTATION_CHANCE) == 1:
            self.stats['food_pref'] += random.uniform(-3, 3)

        if self.mother.generation > self.father.generation:
            self.generation = self.mother.generation + 1
        else:
            self.generation = self.father.generation + 1

        if self.stats['race'] < 1:
            self.stats['race'] = 1
        if self.stats['food_pref'] < 1:
            self.stats['food_pref'] = 1
        if self.stats['race'] > 340:
            self.stats['race'] = 340
        if self.stats['food_pref'] < 150:
            self.stats['food_pref'] = 150

    def attack(self):
        self.health['cell_size'] += 0.01

    def injured(self, damage):
        self.health['cell_size'] -= ((0.05 * damage) / self.stats['defence'])
        self.health['injured'] += 1
