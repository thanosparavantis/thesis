import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from Game import Game


class GameStatistics:
    def __init__(self, game: Game):
        self._game = game
        self._blue_fitness = []
        self._red_fitness = []
        self._figure = None
        self._axes = None

    def add_blue_fitness(self, value):
        self._blue_fitness.append(value)

    def add_red_fitness(self, value):
        self._red_fitness.append(value)

    def render(self) -> None:
        if self._figure is None:
            self._figure, self._axes = plt.subplots()  # type: Figure, Axes

        plt.ion()
        plt.show()
        self._axes.cla()

        blue_player = self._game.get_player(Game.BluePlayer)
        blue_color = blue_player.get_tile_color()
        red_player = self._game.get_player(Game.RedPlayer)
        red_color = red_player.get_tile_color()

        self._figure.suptitle('Game Statistics')

        if len(self._blue_fitness):
            y = self._blue_fitness[-50:]
            x = np.arange(len(y))
            self._axes.plot(x, y, color=blue_color, alpha=0.8)
            self._axes.scatter(x, y, marker='.', c=blue_color)

        if len(self._red_fitness):
            y = self._red_fitness[-50:]
            x = np.arange(len(y))
            self._axes.plot(x, y, color=red_color, alpha=0.8)
            self._axes.scatter(x, y, marker='.', c=red_color)

        plt.pause(0.001)
