import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle


class GameMap:
    def __init__(self, game):
        self._game = game
        self._map_fig = None
        self._map_ax = None

    def render(self, title, subtitle):
        from game import Game

        if self._map_fig is None:
            self._map_fig, self._map_ax = plt.subplots()  # type: Figure, Axes

        self._map_ax.cla()

        rmap_owners = np.flip(self._game.get_map_owners(), axis=0)
        rmap_troops = np.flip(self._game.get_map_troops(), axis=0)

        plt.ion()
        plt.show()

        self._map_fig.suptitle(title)
        plt.setp(self._map_ax.get_xticklabels(), visible=False)
        plt.setp(self._map_ax.get_yticklabels(), visible=False)
        self._map_ax.tick_params(axis='both', which='both', length=0)

        self._map_ax.set_title(subtitle)
        self._map_ax.set_aspect('equal')
        self._map_ax.set_xticks(range(1, Game.MapWidth + 1))
        self._map_ax.set_yticks(range(1, Game.MapHeight + 1))

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile_owner = self._game.get_player(rmap_owners[i, j])
                tile_troops = rmap_troops[i, j]

                tile = Rectangle((j, i), 1, 1, color=tile_owner.get_tile_color(), alpha=tile_owner.get_tile_alpha())
                self._map_ax.add_patch(tile)

                if tile_troops != 0:
                    self._map_ax.text(
                        j + 0.5,
                        i + 0.6,
                        tile_troops,
                        alpha=0.8,
                        fontsize='medium',
                        horizontalalignment='center',
                        verticalalignment='center')

                self._map_ax.text(
                    j + 0.5,
                    i + 0.3,
                    f'({Game.MapWidth - 1 - i}, {j})',
                    alpha=0.2,
                    fontsize='medium',
                    horizontalalignment='center',
                    verticalalignment='center')

        plt.pause(0.001)
