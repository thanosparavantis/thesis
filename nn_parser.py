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

    def decode_state(self, output):
        from game import Game
        output = np.round(output).astype('uint8')

        my_tiles = self._game.get_tiles(self._game.get_player_id())

        tile_id_bits = output[:6]
        tile_id = self.parse_int(tile_id_bits)
        tile_adj_bits = output[6:9]
        tile_adj = self.parse_int(tile_adj_bits)
        troops_bits = output[9:]
        troops = min(self.parse_int(troops_bits), 20) + 1

        tile_A = None
        tile_B = None

        if tile_id < len(my_tiles):
            tile_A = my_tiles[tile_id]

            adjacent = [
                (tile_A[0] - 1, tile_A[1] - 1),
                (tile_A[0] - 1, tile_A[1]),
                (tile_A[0] - 1, tile_A[1] + 1),
                (tile_A[0], tile_A[1] - 1),
                (tile_A[0], tile_A[1] + 1),
                (tile_A[0] + 1, tile_A[1] + 1),
                (tile_A[0] + 1, tile_A[1]),
                (tile_A[0] + 1, tile_A[1] - 1)
            ]

            tile_B = adjacent[tile_adj]

        move_type = Game.InvalidMove

        if tile_A and tile_B:
            production_valid = self._game.is_production_move_valid(tile_A)
            attack_valid = self._game.is_attack_move_valid(tile_A, tile_B, troops)
            transport_valid = self._game.is_transport_move_valid(tile_A, tile_B, troops)

            if production_valid:
                tile_B = tile_A
                troops = 0
                move_type = Game.ProductionMove
            elif attack_valid:
                move_type = Game.AttackMove
            elif transport_valid:
                move_type = Game.TransportMove

        state = {
            "move_type": move_type,
            "tile_A": tile_A,
            "tile_B": tile_B,
            "troops": troops
        }

        return state

    @staticmethod
    def parse_int(encoded_state):
        return int(''.join([str(bit) for bit in encoded_state]), 2)
