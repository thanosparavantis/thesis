import math
from typing import List, Tuple, Dict

from numpy import ndarray

from Game import Game


class StateParser:
    def __init__(self, game: Game):
        self._game = game

    def encode_state(self) -> List[int]:
        inputs = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile = (i, j)
                troops = self._game.get_tile_troops(tile)
                owner = self._game.get_tile_owner(tile)
                sign = 0

                if owner == Game.BluePlayer:
                    sign = 1
                elif owner == Game.RedPlayer:
                    sign = -1

                inputs.append((sign * troops) / Game.TileTroopMax)

        return inputs

    def decode_state(self, output: ndarray) -> Dict:
        tile_a_output = output[0]
        tile_b_output = output[1]
        troops_output = output[2]

        player_id = self._game.get_player_id()
        tiles = self._game.get_tiles(player_id)
        tiles = list(filter(self._selectable_tiles_A, tiles))
        tile_count = len(tiles)

        tile_A_idx = math.ceil(tile_a_output * (tile_count - 1))
        tile_A = tiles[tile_A_idx]

        prod_valid = self._game.is_production_move_valid(tile_A)

        tiles_adj = self._game.get_tile_adj(tile_A)
        tiles_adj = list(filter(self._selectable_tiles_B, tiles_adj))

        if prod_valid or len(tiles_adj) == 0:
            tiles_adj = [tile_A] + tiles_adj

        tiles_adj_count = len(tiles_adj)
        tile_B_idx = math.ceil(tile_b_output * (tiles_adj_count - 1))
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

        if tile_A == tile_B and prod_valid:
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

        if move_type == Game.InvalidMove:
            self._report_invalid_move(player_move)

        return player_move

    def _report_invalid_move(self, move):
        tile_A = move['tile_A']
        tile_B = move['tile_B']
        troops = move['troops']
        player_id = self._game.get_player_id()
        enemy_id = self._game.get_enemy_id()

        player_tiles = self._game.get_tiles(player_id)
        player_info = dict()
        for tile in player_tiles:
            troops = self._game.get_tile_troops(tile)
            player_info[tile] = troops

        enemy_tiles = self._game.get_tiles(enemy_id)
        enemy_info = dict()
        for tile in enemy_tiles:
            troops = self._game.get_tile_troops(tile)
            enemy_info[tile] = troops

        print(50 * '=')
        print('Invalid Move')
        print(50 * '=')
        print(f'Tile A: {tile_A}')
        print(f'Tile B: {tile_B}')
        print(f'Troops: {troops}')
        print(f'Player ID: {player_id}')
        print(f'Player Info: {player_info}')
        print(f'Enemy ID: {enemy_id}')
        print(f'Enemy Info: {enemy_info}')

    def _selectable_tiles_A(self, tile: Tuple[int, int]) -> bool:
        troops = self._game.get_tile_troops(tile)

        if troops < Game.TileTroopMax:
            return True

        player_id = self._game.get_player_id()
        tiles_adj = self._game.get_tile_adj(tile)
        blocked = 0

        for tile_adj in tiles_adj:
            troops_adj = self._game.get_tile_troops(tile_adj)
            neighbour_id = self._game.get_tile_owner(tile_adj)

            if neighbour_id == player_id and troops_adj == Game.TileTroopMax:
                blocked += 1

        return blocked != len(tiles_adj)

    def _selectable_tiles_B(self, tile: Tuple[int, int]) -> bool:
        player_id = self._game.get_player_id()
        owner_id = self._game.get_tile_owner(tile)
        troops = self._game.get_tile_troops(tile)

        return player_id != owner_id or troops != Game.TileTroopMax

    @staticmethod
    def parse_int(encoded_state: ndarray) -> int:
        return int(''.join([str(bit) for bit in encoded_state]), 2)
