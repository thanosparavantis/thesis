from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from Game import Game


class GameStatistics:
    def __init__(self, game: Game):
        self._game = game
        self._blue_fitness = []
        self._red_fitness = []
        self._figure = None
        self._axis = None

    def add_blue_fitness(self, value):
        self._blue_fitness.append(value)

    def add_red_fitness(self, value):
        self._red_fitness.append(value)

    def render(self) -> None:
        if self._figure is None:
            self._figure, self._axis = plt.subplots()  # type: Figure, Axes

        self._axis.cla()
        plt.ion()
        plt.show()

        blue_player = self._game.get_player(Game.BluePlayer)
        blue_color = blue_player.get_tile_color()
        red_player = self._game.get_player(Game.RedPlayer)
        red_color = red_player.get_tile_color()

        self._figure.suptitle('Game Statistics')

        if len(self._blue_fitness):
            x, y = self.get_graph_data(self._blue_fitness)
            self._axis.plot(x, y, color=blue_color, alpha=0.8)
            self._axis.scatter(x, y, marker='.', c=blue_color)

        if len(self._red_fitness):
            x, y = self.get_graph_data(self._red_fitness)
            self._axis.plot(x, y, color=red_color, alpha=0.8)
            self._axis.scatter(x, y, marker='.', c=red_color)

        plt.pause(0.001)

    def get_graph_data(self, sample_array: List[int]) -> Tuple[List[int], List[int]]:
        sample_array = sample_array[-100:]
        x = [i for i in range(len(sample_array))]
        y = sample_array
        return x, y
