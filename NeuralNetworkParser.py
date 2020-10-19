import math
from typing import Dict, List, Tuple

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

    def decode_state_m1(self, output: ndarray) -> Dict:
        possible_moves = []

        for tile_A in self._game.get_tiles(self._game.get_player_id()):
            if self._game.is_production_move_valid(tile_A):
                possible_moves.append({
                    'move_type': Game.ProductionMove,
                    'tile_A': tile_A,
                    'tile_B': tile_A,
                    'troops': 0
                })

            for tile_B in self._game.get_tile_adj(tile_A):
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

    def decode_state_m2(self, output: ndarray):
        tile_a_output = output[0]
        tile_b_output = output[1]
        troops_output = output[2]

        player_id = self._game.get_player_id()
        tiles = self._game.get_tiles(player_id)
        tiles = list(filter(self._tile_is_not_blocked, tiles))
        tile_count = len(tiles)

        tile_A_idx = math.ceil(tile_a_output * (tile_count - 1))
        tile_A = tiles[tile_A_idx]

        tiles_adj = self._game.get_tile_adj(tile_A)
        tiles_adj = list(filter(self._tile_is_not_full, tiles_adj))
        tiles_adj_count = len(tiles_adj)
        tile_B_idx = math.ceil(tile_b_output * (tiles_adj_count - 1))

        if len(tiles_adj) == 0:
            tile_B = tile_A
        else:
            tile_B = tiles_adj[tile_B_idx]

        tile_A_troops = self._game.get_tile_troops(tile_A)
        tile_B_troops = self._game.get_tile_troops(tile_B)
        tile_B_owner_id = self._game.get_tile_owner(tile_B)

        if tile_B_owner_id == player_id:
            troops_max = abs(tile_A_troops - tile_B_troops)
        else:
            troops_max = tile_A_troops

        troops = 1 + math.ceil(troops_output * (troops_max - 1))

        prod_valid = self._game.is_production_move_valid(tile_A)
        att_valid = self._game.is_attack_move_valid(tile_A, tile_B, troops)
        trans_valid = self._game.is_transport_move_valid(tile_A, tile_B, troops)

        if prod_valid and not self._is_tile_maxed(tile_A):
            move_type = Game.ProductionMove
        elif att_valid:
            move_type = Game.AttackMove
        elif trans_valid:
            move_type = Game.TransportMove
        else:
            move_type = Game.InvalidMove

        player_move = {
            'move_type': move_type,
            'tile_A': tile_A,
            'tile_B': tile_B,
            'troops': troops
        }

        return player_move

    def _is_tile_maxed(self, tile: Tuple[int, int]) -> bool:
        troops = self._game.get_tile_adj(tile)
        return troops == (Game.TileTroopMax - 1)

    def _tile_is_not_blocked(self, tile: Tuple[int, int]) -> bool:
        troops = self._game.get_tile_troops(tile)

        if troops < Game.TileTroopMax:
            return True

        player_id = self._game.get_player_id()
        adjacent_tiles = self._game.get_tile_adj(tile)
        neighbours_blocked = 0

        for neighbour_tile in adjacent_tiles:
            neighbour_troops = self._game.get_tile_troops(neighbour_tile)
            neighbour_owner_id = self._game.get_tile_owner(neighbour_tile)

            if neighbour_owner_id == player_id and neighbour_troops == Game.TileTroopMax:
                neighbours_blocked += 1

        return neighbours_blocked != len(adjacent_tiles)

    def _tile_is_not_full(self, tile: Tuple[int, int]) -> bool:
        player_id = self._game.get_player_id()
        owner_id = self._game.get_tile_owner(tile)
        troops = self._game.get_tile_troops(tile)

        return player_id != owner_id or troops != Game.TileTroopMax

    @staticmethod
    def parse_int(encoded_state: ndarray) -> int:
        return int(''.join([str(bit) for bit in encoded_state]), 2)
