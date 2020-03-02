import math
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from sklearn import preprocessing


class Game:
    # The nature player that owns the tiles inbetween the two players
    NaturePlayer = 0

    # The blue player who starts on the upper left corner
    BluePlayer = 1

    # The red player who starts on the lower right corner
    RedPlayer = 2

    # The number of tiles on the x-axis
    MapWidth = 6

    # The number of tiles on the y-axis
    MapHeight = 6

    # The minimum amount of troops for each tile, attack and transfer
    TileTroopMin = 1

    # The maximum amount of troops for each tile, attack and transfer
    TileTroopMax = 20

    # The probability of a soldier spawning in a tile owned by nature
    NatureTroopProbability = 0.1

    # The amount of moves before a player's state is declared stale
    MaxMoves = 10

    def __init__(self):
        self._players = None
        self._map_owners = None
        self._map_troops = None
        self._player_id = None
        self._round = None
        self._moves = None
        self.reset_game()
        self._map_fig = None
        self._map_ax = None
        self._scaler = preprocessing.MinMaxScaler()

    def reset_game(self):
        from player import Player

        self._players = [
            Player(name='nature',
                   cursor_a=[0, 0],
                   cursor_b=[0, 0],
                   tile_color='#CBCBC9',
                   tile_alpha=0.2),

            Player(name='blue',
                   cursor_a=[0, 0],
                   cursor_b=[0, 0],
                   tile_color='#2A8FBD',
                   tile_alpha=0.5),

            Player(name='red',
                   cursor_a=[Game.MapWidth - 1, Game.MapHeight - 1],
                   cursor_b=[Game.MapWidth - 1, Game.MapHeight - 1],
                   tile_color='#B40406',
                   tile_alpha=0.5),
        ]

        self._map_owners = np.zeros((Game.MapWidth, Game.MapHeight), dtype='uint8')
        self._map_owners[0, 0] = Game.BluePlayer
        self._map_owners[Game.MapWidth - 1, Game.MapHeight - 1] = Game.RedPlayer
        self._map_troops = np.ones_like(self._map_owners)
        self._player_id = Game.BluePlayer
        self.reset_round()
        self.reset_moves()

    def change_player_id(self):
        self._player_id = Game.RedPlayer if self._player_id == Game.BluePlayer else Game.BluePlayer

    def get_player_id(self):
        return self._player_id

    def get_player(self, player_id):
        return self._players[player_id]

    def get_round(self):
        return self._round

    def reset_round(self):
        self._round = 1

    def increase_round(self):
        self._round += 1

    def get_moves(self):
        return self._moves

    def reset_moves(self):
        self._moves = Game.MaxMoves

    def make_move(self):
        self._moves -= 1

    def has_moves(self):
        return self._moves > 0

    def production_move(self):
        produced_once = False

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile_owner = self._map_owners[i, j]
                troops = self._map_troops[i, j]

                tile_can_produce = tile_owner == self._player_id and troops < Game.TileTroopMax
                tile_is_nature = tile_owner == Game.NaturePlayer and random.random() <= Game.NatureTroopProbability and troops < Game.TileTroopMax

                if tile_can_produce:
                    self._map_troops[i, j] += 1

                    if not produced_once:
                        player = self._players[self._player_id]
                        player.increase_production()
                        produced_once = True
                elif tile_is_nature:
                    self._map_troops[i, j] += 1

    def is_production_move_valid(self):
        return self.get_troop_count(self._player_id) % Game.TileTroopMax != 0

    def attack_move(self):
        from player import Player
        player = self._players[self._player_id]
        cursor_a = player.get_cursor(Player.CursorA)
        cursor_b = player.get_cursor(Player.CursorB)
        my_tiles = self.get_tiles(self._player_id)
        my_adj_tiles = self.get_tiles_adj(self._player_id)
        source_cursor = None
        target_cursor = None

        if cursor_a in my_tiles:
            source_cursor = cursor_a
        elif cursor_a in my_adj_tiles:
            target_cursor = cursor_a

        if source_cursor is None and cursor_b in my_tiles:
            source_cursor = cursor_b
        elif target_cursor is None and cursor_b in my_adj_tiles:
            target_cursor = cursor_b

        s_i, s_j = source_cursor
        t_i, t_j = target_cursor

        attackers = math.floor(self._map_troops[s_i, s_j] / 2)
        defenders = self._map_troops[t_i, t_j]

        self._map_troops[s_i, s_j] -= attackers

        if defenders < attackers:
            self._map_owners[t_i, t_j] = self._player_id
            self._map_troops[t_i, t_j] = attackers - defenders
            player.increase_attacks_succeeded()
        else:
            self._map_troops[t_i, t_j] = defenders - attackers
            player.increase_attacks_failed()

        player.increase_attacks()

    def is_attack_move_valid(self):
        from player import Player
        player = self._players[self._player_id]
        cursor_a = player.get_cursor(Player.CursorA)
        cursor_b = player.get_cursor(Player.CursorB)
        my_tiles = self.get_tiles(self._player_id)
        my_adj_tiles = self.get_tiles_adj(self._player_id)
        source_cursor = None
        target_cursor = None

        if cursor_a in my_tiles:
            source_cursor = cursor_a
        elif cursor_a in my_adj_tiles:
            target_cursor = cursor_a

        if source_cursor is None and cursor_b in my_tiles:
            source_cursor = cursor_b
        elif target_cursor is None and cursor_b in my_adj_tiles:
            target_cursor = cursor_b

        if source_cursor is None:
            return False

        if target_cursor is None:
            return False

        s_i, s_j = source_cursor
        attackers = math.floor(self._map_troops[s_i, s_j] / 2)

        if attackers < Game.TileTroopMin:
            return False

        return True

    def transport_move(self):
        from player import Player
        player = self._players[self._player_id]
        source_cursor = player.get_cursor(Player.CursorA)
        target_cursor = player.get_cursor(Player.CursorB)
        s_i, s_j = source_cursor
        t_i, t_j = target_cursor

        transport = math.floor(self._map_troops[s_i, s_j] / 2)

        self._map_troops[s_i, s_j] -= transport
        self._map_troops[t_i, t_j] += transport

        player = self._players[self._player_id]
        player.increase_transports()

    def is_transport_move_valid(self):
        from player import Player
        player = self._players[self._player_id]
        source_cursor = player.get_cursor(Player.CursorA)
        target_cursor = player.get_cursor(Player.CursorB)
        my_tiles = self.get_tiles(self._player_id)

        if source_cursor not in my_tiles:
            return False

        if target_cursor not in my_tiles:
            return False

        if source_cursor == target_cursor:
            return False

        s_i, s_j = source_cursor
        t_i, t_j = target_cursor

        transport = math.floor(self._map_troops[s_i, s_j] / 2)

        if transport < Game.TileTroopMin:
            return False

        if self._map_troops[t_i, t_j] + transport > Game.TileTroopMax:
            return False

        return True

    def render_map(self, title, subtitle):
        from player import Player

        if self._map_fig is None:
            self._map_fig, self._map_ax = plt.subplots()  # type: Figure, Axes

        self._map_ax.cla()

        player = self._players[self._player_id]
        cursor_a = player.get_cursor(Player.CursorA)
        cursor_b = player.get_cursor(Player.CursorB)
        s_i = Game.MapWidth - cursor_a[0] - 1
        s_j = cursor_a[1]
        t_i = Game.MapHeight - cursor_b[0] - 1
        t_j = cursor_b[1]

        rmap_owners = np.flip(self._map_owners, axis=0)
        rmap_troops = np.flip(self._map_troops, axis=0)

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
                tile_owner = self._players[rmap_owners[i, j]]
                tile_troops = rmap_troops[i, j]

                if i == s_i and j == s_j and cursor_a == cursor_b:
                    tile = Rectangle((j, i), 1, 1, facecolor=tile_owner.get_tile_color(), alpha=0.7)
                    cursor_text = 'AB'
                    cursor_color = 'white' if rmap_owners[i, j] == self._player_id else player.get_tile_color()
                    self._map_ax.text(j + 0.8, i + 0.8, cursor_text, color=cursor_color, fontsize='medium', fontweight='semibold', horizontalalignment='center', verticalalignment='center')
                elif i == s_i and j == s_j:
                    tile = Rectangle((j, i), 1, 1, facecolor=tile_owner.get_tile_color(), alpha=0.7)
                    cursor_text = 'A'
                    cursor_color = 'white' if rmap_owners[i, j] == self._player_id else player.get_tile_color()
                    self._map_ax.text(j + 0.8, i + 0.8, cursor_text, color=cursor_color, fontsize='medium', fontweight='semibold', horizontalalignment='center', verticalalignment='center')
                elif i == t_i and j == t_j:
                    tile = Rectangle((j, i), 1, 1, facecolor=tile_owner.get_tile_color(), alpha=0.7)
                    cursor_text = 'B'
                    cursor_color = 'white' if rmap_owners[i, j] == self._player_id else player.get_tile_color()
                    self._map_ax.text(j + 0.8, i + 0.8, cursor_text, color=cursor_color, fontsize='medium', fontweight='semibold', horizontalalignment='center', verticalalignment='center')
                else:
                    tile = Rectangle((j, i), 1, 1, color=tile_owner.get_tile_color(), alpha=tile_owner.get_tile_alpha())

                self._map_ax.add_patch(tile)

                if tile_troops != 0:
                    self._map_ax.text(j + 0.5, i + 0.6, tile_troops, alpha=0.8, fontsize='medium', horizontalalignment='center', verticalalignment='center')

                self._map_ax.text(j + 0.5, i + 0.3, f'({5 - i}, {j})', alpha=0.2, fontsize='medium', horizontalalignment='center', verticalalignment='center')

        plt.pause(0.001)

    def create_input(self):
        from player import Player

        player = self._players[self._player_id]
        moves = self._moves
        g_round = self._round
        cursor_a = player.get_cursor(Player.CursorA)
        cursor_b = player.get_cursor(Player.CursorB)

        inputs = [self._player_id, moves, g_round, cursor_a[0], cursor_a[1], cursor_b[0], cursor_b[1]]

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                inputs.append(self._map_owners[i, j])

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                inputs.append(self._map_troops[i, j])

        inputs = np.array(inputs)

        scaled_input = inputs.reshape((-1, 1))
        scaled_input = self._scaler.fit_transform(scaled_input)
        scaled_input = scaled_input.flatten()

        return scaled_input

    def parse_output(self, output):
        return np.round(output).astype('uint8')

    def get_tile_count(self, player_id):
        return len(self.get_tiles(player_id))

    def get_troop_count(self, player_id):
        troops = 0

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    troops += self._map_troops[i, j]

        return int(troops)

    def get_tiles(self, player_id):
        tiles = set()

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    tiles.add((i, j))

        return tiles

    def get_tiles_adj(self, player_id):
        adjacent = set()

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    adjacent.add((i + 1, j))
                    adjacent.add((i, j + 1))
                    adjacent.add((i - 1, j))
                    adjacent.add((i, j - 1))
                    adjacent.add((i + 1, j + 1))
                    adjacent.add((i - 1, j - 1))

        adjacent_valid = set()

        for item in adjacent:
            i, j = item

            if 0 <= i <= Game.MapWidth - 1 and 0 <= j <= Game.MapHeight - 1 and self._map_owners[i, j] != player_id:
                adjacent_valid.add(item)

        return adjacent_valid

    def get_troops_at(self, cursor):
        return self._map_troops[cursor[0], cursor[1]]
