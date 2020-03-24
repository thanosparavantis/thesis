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
        output = np.round(output).astype('uint8')

        move_type = self.parse_int(output[0:2])
        tile_A = (self.parse_int(output[2:5]), self.parse_int(output[5:8]))
        tile_B = (self.parse_int(output[8:11]), self.parse_int(output[11:14]))
        troops = self.parse_int(output[14:19])

        return {"move_type": move_type, "tile_A": tile_A, "tile_B": tile_B, "troops": troops}

    @staticmethod
    def parse_int(encoded_state):
        return int(''.join([str(bit) for bit in encoded_state]), 2)
