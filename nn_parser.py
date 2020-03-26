import random

import numpy as np
from sklearn import preprocessing


class NeuralNetworkParser:
    def __init__(self, game):
        from game import Game

        self._game = game  # type: Game
        self._scaler = preprocessing.MinMaxScaler()

    def encode_state(self):
        from game import Game

        inputs = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                sign = 1 if self._game.get_map_owners()[i, j] == self._game.get_player_id() else -1
                troops = self._game.get_map_troops()[i, j].item()
                inputs.append(sign * troops)

        return inputs

    def decode_output(self, output):
        from game import Game
        output = np.round(output).astype('uint8')

        my_tiles = self._game.get_tiles(self._game.get_player_id())
        my_tiles_adj = self._game.get_tiles_adj(self._game.get_player_id())

        move_type = Game.InvalidMove
        tile_id = self.parse_int(output[2:8])
        tile_adj = self.parse_int(output[8:11])
        troops = self.parse_int(output[11:16]) + 1

        tile_A = None
        tile_B = None

        if tile_id < len(my_tiles):
            tile_A = my_tiles[tile_id]
        # else:
        #     tile_A = my_tiles[0]

            adjacent = [
                (tile_A[0] - 1, tile_A[1] + 1),
                (tile_A[0], tile_A[1] + 1),
                (tile_A[0] + 1, tile_A[1] + 1),
                (tile_A[0] - 1, tile_A[1]),
                (tile_A[0] + 1, tile_A[1]),
                (tile_A[0] - 1, tile_A[1] - 1),
                (tile_A[0], tile_A[1] - 1),
                (tile_A[0] + 1, tile_A[1] - 1)
            ]

            tile_B = adjacent[tile_adj]

        # idx = 0
        # while tile_B not in my_tiles and tile_B not in my_tiles_adj:
        #     tile_B = adjacent[idx]
        #     idx += 1

        if tile_A and tile_B:
            if tile_A == tile_B and self._game.is_production_move_valid(tile_A):
                move_type = Game.ProductionMove
            elif tile_A in my_tiles and tile_B in my_tiles_adj and self._game.is_attack_move_valid(tile_A, tile_B, troops):
                move_type = Game.AttackMove
            elif tile_A in my_tiles and tile_B in my_tiles and self._game.is_transport_move_valid(tile_A, tile_B, troops):
                move_type = Game.TransportMove

        player_move = {"move_type": move_type, "tile_A": tile_A, "tile_B": tile_B, "troops": troops}

        return player_move

    @staticmethod
    def parse_int(encoded_state):
        return int(''.join([str(bit) for bit in encoded_state]), 2)
