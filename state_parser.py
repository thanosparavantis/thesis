import math
import random
import sys
from typing import List, Dict, Tuple


class StateParser:
    def __init__(self):
        self.game = None

    def encode_state(self) -> List[int]:
        from game import Game

        inputs = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile = (i, j)
                troops = self.game.get_tile_troops(tile)
                owner = self.game.get_tile_owner(tile)
                sign = 0

                if owner == Game.BluePlayer:
                    sign = 1
                elif owner == Game.RedPlayer:
                    sign = -1

                inputs.append((sign * troops) / Game.TileTroopMax)

        return inputs

    def decode_prod_flag(self, number: float) -> bool:
        return number <= 0.5

    def decode_tile(self, number: float) -> Tuple[int, int]:
        from game import Game

        lb = 0
        step = 1 / (Game.MapSize - 1)
        idx = 0
        tile = 0

        while lb <= 1.0:
            ub = lb + step
            if lb <= number <= ub:
                tile = self.game.get_tile_coords(idx)
            lb = ub
            idx += 1

        return tile

    def decode_troops(self, number: float) -> int:
        from game import Game

        lb = 0
        step = 1 / Game.TileTroopMax
        idx = 1
        troops = 1

        while lb <= 1.0:
            ub = lb + step
            if lb <= number <= ub:
                troops = idx
            lb = ub
            idx += 1

        return troops

    def get_next_moves(self) -> List[Dict]:
        from game import Game

        moves = []
        player_id = self.game.get_player_id()

        for tile in self.game.get_tiles(player_id):
            if self.game.is_production_move_valid(tile):
                moves.append({
                    'move_type': Game.ProductionMove,
                    'source_tile': tile,
                    'target_tile': tile,
                    'troops': 1
                })

            max_troops = self.game.get_tile_troops(tile)

            for tile_adj in self.game.get_tile_adj(tile):
                for troops in range(Game.TileTroopMin, max_troops + 1):
                    if self.game.is_attack_move_valid(tile, tile_adj, troops):
                        moves.append({
                            'move_type': Game.AttackMove,
                            'source_tile': tile,
                            'target_tile': tile_adj,
                            'troops': troops
                        })

                    if self.game.is_transport_move_valid(tile, tile_adj, troops):
                        moves.append({
                            'move_type': Game.TransportMove,
                            'source_tile': tile,
                            'target_tile': tile_adj,
                            'troops': troops
                        })

        random.shuffle(moves)
        return moves

    def guide_move(self, player_move: Dict) -> Dict:
        moves = self.get_next_moves()
        best_move = None
        distance = sys.maxsize

        for possible_move in moves:
            source_1 = self.game.get_tile_number(player_move['source_tile'])
            target_1 = self.game.get_tile_number(player_move['target_tile'])
            troops_1 = player_move['troops']
            source_2 = self.game.get_tile_number(possible_move['source_tile'])
            target_2 = self.game.get_tile_number(possible_move['target_tile'])
            troops_2 = possible_move['troops']

            calc_distance = math.sqrt(
                ((source_1 - source_2) ** 2) + ((target_1 - target_2) ** 2) + ((troops_1 - troops_2) ** 2)
            )

            if calc_distance < distance:
                best_move = possible_move
                distance = calc_distance

        player_move['move_type'] = best_move['move_type']
        player_move['source_tile'] = best_move['source_tile']
        player_move['target_tile'] = best_move['target_tile']
        player_move['troops'] = best_move['troops']
        player_move['guided'] = True

        return player_move

    def decode_state(self, output: list) -> Dict:
        from game import Game

        prod_flag = self.decode_prod_flag(output[0])
        source_tile = self.decode_tile(output[1])

        if prod_flag:
            target_tile = source_tile
            troops = 1
        else:
            target_tile = self.decode_tile(output[2])
            troops = self.decode_troops(output[3])

        if prod_flag and self.game.is_production_move_valid(source_tile):
            move_type = Game.ProductionMove
        elif self.game.is_attack_move_valid(source_tile, target_tile, troops):
            move_type = Game.AttackMove
        elif self.game.is_transport_move_valid(source_tile, target_tile, troops):
            move_type = Game.TransportMove
        else:
            move_type = Game.IdleMove

        player_move = {
            'move_type': move_type,
            'source_tile': source_tile,
            'target_tile': target_tile,
            'troops': troops,
            'guided': False,
        }

        if move_type == Game.IdleMove:
            player_move = self.guide_move(player_move)

        return player_move
