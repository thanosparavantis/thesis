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
        possible_moves = []

        for tile_A in self._game.get_tiles(self._game.get_player_id()):
            if self._game.is_production_move_valid(tile_A):
                possible_moves.append({
                    'move_type': Game.ProductionMove,
                    'tile_A': tile_A,
                    'tile_B': tile_A,
                    'troops': 0
                })

            for tile_B in self._game.get_tiles_adj(tile_A):
                for troops in range(Game.TileTroopMax):
                    if self._game.is_attack_move_valid(tile_A, tile_B, troops):
                        possible_moves.append({
                            'move_type': Game.AttackMove,
                            'tile_A': tile_A,
                            'tile_B': tile_B,
                            'troops': troops
                        })

                    if self._game.is_transport_move_valid(tile_A, tile_B, troops):
                        possible_moves.append({
                            'move_type': Game.TransportMove,
                            'tile_A': tile_A,
                            'tile_B': tile_B,
                            'troops': troops
                        })

        move = possible_moves[math.ceil(output[0] * (len(possible_moves) - 1))]
        return move

    @staticmethod
    def parse_int(encoded_state: ndarray) -> int:
        return int(''.join([str(bit) for bit in encoded_state]), 2)
