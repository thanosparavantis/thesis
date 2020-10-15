import math
from typing import Dict, List

from numpy import ndarray

from Game import Game


class NeuralNetworkParser:
    def __init__(self, game: Game):
        self._game = game

    def encode_state(self) -> List[int]:
        inputs = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                sign = 1 if self._game.get_map_owners()[i, j] == self._game.get_player_id() else -1
                troops = self._game.get_map_troops()[i, j].item()
                inputs.append((sign * troops) / Game.TileTroopMax)

        return inputs

    def decode_state(self, output: ndarray) -> Dict:
        player_id = self._game.get_player_id()
        player_tiles = self._game.get_tiles(player_id)
        player_tiles_count = len(player_tiles)

        tile_A = player_tiles[math.ceil(output[0] * (player_tiles_count - 1))]

        adjacent_tiles = self._game.get_tiles_adj(tile_A)
        adjacent_tiles_count = len(adjacent_tiles)
        tile_B = adjacent_tiles[math.ceil(output[1] * (adjacent_tiles_count - 1))]

        troop_count = self._game.get_tile_troops(tile_A)
        troops = math.ceil(output[2] * troop_count)

        production_valid = self._game.is_production_move_valid(tile_A)
        attack_valid = self._game.is_attack_move_valid(tile_A, tile_B, troops)
        transport_valid = self._game.is_transport_move_valid(tile_A, tile_B, troops)

        if troops == 0 and production_valid:
            move_type = Game.ProductionMove
        elif attack_valid:
            move_type = Game.AttackMove
        elif transport_valid:
            move_type = Game.TransportMove
        else:
            move_type = Game.InvalidMove

        state = {
            "move_type": move_type,
            "tile_A": tile_A,
            "tile_B": tile_B,
            "troops": troops
        }

        print(player_id, state)

        return state

    @staticmethod
    def parse_int(encoded_state: ndarray) -> int:
        return int(''.join([str(bit) for bit in encoded_state]), 2)
