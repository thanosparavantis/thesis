import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, RegularPolygon


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

        # player = self._game.get_player(self._game.get_player_id())
        # cursor_a = player.get_cursor(GamePlayer.CursorA)
        # cursor_b = player.get_cursor(GamePlayer.CursorB)
        # s_i = Game.MapWidth - cursor_a[0] - 1
        # s_j = cursor_a[1]
        # t_i = Game.MapHeight - cursor_b[0] - 1
        # t_j = cursor_b[1]

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

        # self._map_ax.add_patch(RegularPolygon((1, 5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((2, 5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((3, 5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((4, 5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((5, 5), 6, 0.6))
        #
        # self._map_ax.add_patch(RegularPolygon((1.5, 4.1), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((2.5, 4.1), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((3.5, 4.1), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((4.5, 4.1), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((5.5, 4.1), 6, 0.6))
        #
        # self._map_ax.add_patch(RegularPolygon((1, 3.2), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((2, 3.2), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((3, 3.2), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((4, 3.2), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((5, 3.2), 6, 0.6))
        #
        # self._map_ax.add_patch(RegularPolygon((1.5, 2.3), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((2.5, 2.3), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((3.5, 2.3), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((4.5, 2.3), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((5.5, 2.3), 6, 0.6))
        #
        # self._map_ax.add_patch(RegularPolygon((1, 1.4), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((2, 1.4), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((3, 1.4), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((4, 1.4), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((5, 1.4), 6, 0.6))
        #
        # self._map_ax.add_patch(RegularPolygon((1.5, 0.5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((2.5, 0.5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((3.5, 0.5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((4.5, 0.5), 6, 0.6))
        # self._map_ax.add_patch(RegularPolygon((5.5, 0.5), 6, 0.6))

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile_owner = self._game.get_player(rmap_owners[i, j])
                tile_troops = rmap_troops[i, j]

                # if i == s_i and j == s_j and cursor_a == cursor_b:
                #     tile = Rectangle((j, i), 1, 1, facecolor=tile_owner.get_tile_color(), alpha=0.7)
                #     cursor_text = 'AB'
                #     cursor_color = 'white' if rmap_owners[i, j] == self._game.get_player_id() else player.get_tile_color()
                #     self._map_ax.text(j + 0.8, i + 0.8, cursor_text, color=cursor_color, fontsize='medium', fontweight='semibold', horizontalalignment='center', verticalalignment='center')
                # elif i == s_i and j == s_j:
                #     tile = Rectangle((j, i), 1, 1, facecolor=tile_owner.get_tile_color(), alpha=0.7)
                #     cursor_text = 'A'
                #     cursor_color = 'white' if rmap_owners[i, j] == self._game.get_player_id() else player.get_tile_color()
                #     self._map_ax.text(j + 0.8, i + 0.8, cursor_text, color=cursor_color, fontsize='medium', fontweight='semibold', horizontalalignment='center', verticalalignment='center')
                # elif i == t_i and j == t_j:
                #     tile = Rectangle((j, i), 1, 1, facecolor=tile_owner.get_tile_color(), alpha=0.7)
                #     cursor_text = 'B'
                #     cursor_color = 'white' if rmap_owners[i, j] == self._game.get_player_id() else player.get_tile_color()
                #     self._map_ax.text(j + 0.8, i + 0.8, cursor_text, color=cursor_color, fontsize='medium', fontweight='semibold', horizontalalignment='center', verticalalignment='center')
                # else:
                #     tile = Rectangle((j, i), 1, 1, color=tile_owner.get_tile_color(), alpha=tile_owner.get_tile_alpha())

                alpha = 1 if rmap_owners[i, j] == self._game.get_player_id() else tile_owner.get_tile_alpha()

                tile = Rectangle((j, i), 1, 1, color=tile_owner.get_tile_color(), alpha=alpha)
                self._map_ax.add_patch(tile)

                if tile_troops != 0:
                    self._map_ax.text(j + 0.5, i + 0.6, tile_troops, alpha=0.8, fontsize='medium', horizontalalignment='center', verticalalignment='center')

                self._map_ax.text(j + 0.5, i + 0.3, f'({Game.MapWidth - 1 - i}, {j})', alpha=0.2, fontsize='medium', horizontalalignment='center', verticalalignment='center')

        plt.pause(0.001)
