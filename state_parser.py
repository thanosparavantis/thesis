from typing import List, Dict, Tuple

from game import Game


class StateParser:
    def __init__(self, game: Game):
        self._game = game

    def encode_state(self) -> List[int]:
        return self._encode_state(self._game)

    def _encode_state(self, game: Game) -> List[int]:
        inputs = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile = (i, j)
                troops = game.get_tile_troops(tile)
                owner = game.get_tile_owner(tile)
                sign = 0

                if owner == Game.BluePlayer:
                    sign = 1
                elif owner == Game.RedPlayer:
                    sign = -1

                inputs.append((sign * troops) / Game.TileTroopMax)

        return inputs

    # =========================================================
    # Map Decoding
    # =========================================================
    # def decode_state(self, output: list) -> (Dict, int):
    #     self._game.get_map_owners()
    #     valid_moves = []
    #     valid_states = []
    #
    #     player_id = self._game.get_player_id()
    #     tiles = self._game.get_tiles(player_id)
    #
    #     for tile in tiles:
    #         tile_troops = self._game.get_tile_troops(tile)
    #
    #         if tile_troops + 1 <= Game.TileTroopMax:
    #             valid_moves.append({
    #                 'move_type': Game.ProductionMove,
    #                 'source_tile': tile,
    #                 'target_tile': None,
    #                 'troops': None
    #             })
    #
    #             temp_game = Game.copy_of(self._game)
    #             temp_game.production_move(tile)
    #             state = self._encode_state(temp_game)
    #             valid_states.append(state)
    #
    #         for tile_adj in self._game.get_tile_adj(tile):
    #             tile_adj_troops = self._game.get_tile_troops(tile_adj)
    #
    #             if tile_adj not in tiles:
    #                 for troops in range(Game.TileTroopMin, tile_troops + 1):
    #                     valid_moves.append({
    #                         'move_type': Game.AttackMove,
    #                         'source_tile': tile,
    #                         'target_tile': tile_adj,
    #                         'troops': troops
    #                     })
    #
    #                     temp_game = Game.copy_of(self._game)
    #                     temp_game.attack_move(tile, tile_adj, troops)
    #                     state = self._encode_state(temp_game)
    #                     valid_states.append(state)
    #
    #             if tile_adj in tiles:
    #                 for troops in range(Game.TileTroopMin, min(Game.TileTroopMax - tile_adj_troops, tile_troops) + 1):
    #                     if self._game.is_transport_move_valid(tile, tile_adj, troops):
    #                         valid_moves.append({
    #                             'move_type': Game.TransportMove,
    #                             'source_tile': tile,
    #                             'target_tile': tile_adj,
    #                             'troops': troops
    #                         })
    #
    #                         temp_game = Game.copy_of(self._game)
    #                         temp_game.transport_move(tile, tile_adj, troops)
    #                         state = self._encode_state(temp_game)
    #                         valid_states.append(state)
    #
    #     selected_move = {
    #         'move_type': Game.InvalidMove,
    #         'source_tile': None,
    #         'target_tile': None,
    #         'troops': None
    #     }
    #
    #     output_state = []
    #
    #     for tile_data in output:
    #         output_state.append(math.ceil(tile_data * Game.TileTroopMax) / Game.TileTroopMax)
    #
    #     for i in range(len(valid_moves)):
    #         valid_move = valid_moves[i]
    #         valid_state = valid_states[i]
    #
    #         if output == valid_state:
    #             selected_move = valid_move
    #             break
    #
    #     diffs = []
    #
    #     for idx, real_value in enumerate(self.encode_state()):
    #         predicted = output_state[idx]
    #
    #         if predicted != real_value:
    #             diffs.append((idx, real_value, predicted))
    #
    #     print(output_state)
    #     matrix_fitness = (Game.MapSize - len(diffs)) / Game.MapSize
    #
    #     return selected_move, matrix_fitness

    # =========================================================
    # All Moves Decoding
    # =========================================================
    # def decode_state(self, output: list) -> Dict:
    #     player_move = self._move_options[math.ceil(output[0] * (len(self._move_options) - 1))]
    #     move_type, source_tile, target_tile, troops = player_move
    #
    #     prod_valid = self._game.is_production_move_valid(source_tile)
    #     att_valid = self._game.is_attack_move_valid(source_tile, target_tile, troops)
    #     trans_valid = self._game.is_transport_move_valid(source_tile, target_tile, troops)
    #
    #     if move_type == Game.ProductionMove and prod_valid:
    #         move_type = Game.ProductionMove
    #     elif move_type == Game.AttackMove and att_valid:
    #         move_type = Game.AttackMove
    #     elif move_type == Game.TransportMove and trans_valid:
    #         move_type = Game.TransportMove
    #     else:
    #         move_type = Game.InvalidMove
    #
    #     player_move = {
    #         'move_type': move_type,
    #         'source_tile': source_tile,
    #         'target_tile': target_tile,
    #         'troops': troops,
    #     }
    #
    #     return player_move

    # =========================================================
    # Possible Move Decoding
    # =========================================================
    # def decode_state(self, output: list) -> Dict:
    #     moves = []
    #     player_id = self._game.get_player_id()
    #     tiles = self._game.get_tiles(player_id)
    #
    #     for tile in tiles:
    #         if self._game.is_production_move_valid(tile):
    #             moves.append({
    #                 'move_type': Game.ProductionMove,
    #                 'source_tile': tile,
    #                 'target_tile': None,
    #                 'troops': None,
    #             })
    #
    #         for tile_adj in self._game.get_tile_adj(tile):
    #             for troops in range(Game.TileTroopMin, Game.TileTroopMax + 1):
    #                 if self._game.is_attack_move_valid(tile, tile_adj, troops):
    #                     moves.append({
    #                         'move_type': Game.AttackMove,
    #                         'source_tile': tile,
    #                         'target_tile': tile_adj,
    #                         'troops': troops,
    #                     })
    #
    #                 if self._game.is_transport_move_valid(tile, tile_adj, troops):
    #                     moves.append({
    #                         'move_type': Game.TransportMove,
    #                         'source_tile': tile,
    #                         'target_tile': tile_adj,
    #                         'troops': troops,
    #                     })
    #
    #     selected_move = moves[math.ceil(output[0] * (len(moves) - 1))]
    #
    #     return selected_move

    # =========================================================
    # Source, Target, Tile Decoding
    # =========================================================
    def decode_state(self, output: list) -> Dict:
        prod_flag = True if output[0] <= 0.5 else False

        lb = 0
        step = 1 / Game.MapSize
        idx = 0
        source_tile = 0

        while lb <= 1.0:
            ub = lb + step
            if lb <= output[1] <= ub:
                source_tile = self._game.get_tile_coords(idx)
            lb = ub
            idx += 1

        lb = 0
        step = 1 / Game.MapSize
        idx = 0
        target_tile = 0

        while lb <= 1.0:
            ub = lb + step
            if lb <= output[2] <= ub:
                target_tile = self._game.get_tile_coords(idx)
            lb = ub
            idx += 1

        lb = 0
        step = 1 / Game.TileTroopMax
        idx = 1
        troops = 1

        while lb <= 1.0:
            ub = lb + step
            if lb <= output[3] <= ub:
                troops = idx
            lb = ub
            idx += 1

        prod_valid = self._game.is_production_move_valid(
            source_tile
        )

        att_valid = self._game.is_attack_move_valid(
            source_tile,
            target_tile,
            troops
        )

        trans_valid = self._game.is_transport_move_valid(
            source_tile,
            target_tile,
            troops
        )

        if prod_flag and prod_valid:
            move_type = Game.ProductionMove
        elif att_valid:
            move_type = Game.AttackMove
        elif trans_valid:
            move_type = Game.TransportMove
        else:
            move_type = Game.IdleMove

        player_move = {
            'move_type': move_type,
            'source_tile': source_tile,
            'target_tile': target_tile,
            'troops': troops,
        }

        return player_move

    # =========================================================
    # Possible Source, Target, Tile Decoding
    # =========================================================
    # def decode_state(self, output: list) -> Dict:
    #     player_id = self._game.get_player_id()
    #     tiles = self._game.get_tiles(player_id)
    #     tiles = list(filter(self._selectable_source_tiles, tiles))
    #     tile_count = len(tiles)
    #
    #     source_tile_idx = math.ceil(output[0] * (tile_count - 1))
    #     source_tile = tiles[source_tile_idx]
    #
    #     prod_valid = self._game.is_production_move_valid(source_tile)
    #
    #     tiles_adj = self._game.get_tile_adj(source_tile)
    #     tiles_adj = list(filter(self._selectable_target_tiles, tiles_adj))
    #
    #     if prod_valid or len(tiles_adj) == 0:
    #         tiles_adj = [source_tile] + tiles_adj
    #
    #     tiles_adj_count = len(tiles_adj)
    #     target_tile_idx = math.ceil(output[1] * (tiles_adj_count - 1))
    #     target_tile = tiles_adj[target_tile_idx]
    #
    #     tile_source_troops = self._game.get_tile_troops(source_tile)
    #     tile_target_troops = self._game.get_tile_troops(target_tile)
    #     tile_target_owner_id = self._game.get_tile_owner(target_tile)
    #
    #     if tile_target_owner_id == player_id:
    #         troops_max = min(Game.TileTroopMax - tile_target_troops, tile_source_troops)
    #     else:
    #         troops_max = tile_source_troops
    #
    #     troops = 1 + math.ceil(output[2] * (troops_max - 1))
    #
    #     prod_valid = self._game.is_production_move_valid(source_tile)
    #     att_valid = self._game.is_attack_move_valid(source_tile, target_tile, troops)
    #     trans_valid = self._game.is_transport_move_valid(source_tile, target_tile, troops)
    #
    #     if source_tile == target_tile and prod_valid:
    #         move_type = Game.ProductionMove
    #     elif att_valid:
    #         move_type = Game.AttackMove
    #     elif trans_valid:
    #         move_type = Game.TransportMove
    #     else:
    #         move_type = Game.InvalidMove
    #
    #     player_move = {
    #         'move_type': move_type,
    #         'source_tile': source_tile,
    #         'target_tile': target_tile,
    #         'troops': troops,
    #     }
    #
    #     return player_move

    @staticmethod
    def _get_move_options() -> List:
        move_options = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile = (i, j)

                move_options.append({
                    'move_type': Game.ProductionMove,
                    'source_tile': tile,
                    'target_tile': None,
                    'troops': None
                })

                tiles_adj = Game.get_tile_adj(tile)

                for tile_adj in tiles_adj:
                    for troops in range(Game.TileTroopMin, Game.TileTroopMax + 1):
                        move_options.append({
                            'move_type': Game.AttackMove,
                            'source_tile': tile,
                            'target_tile': tile_adj,
                            'troops': troops
                        })

                        move_options.append({
                            'move_type': Game.TransportMove,
                            'source_tile': tile,
                            'target_tile': tile_adj,
                            'troops': troops
                        })

        return move_options

    def _selectable_source_tiles(self, tile: Tuple[int, int]) -> bool:
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

    def _selectable_target_tiles(self, tile: Tuple[int, int]) -> bool:
        player_id = self._game.get_player_id()
        owner_id = self._game.get_tile_owner(tile)
        troops = self._game.get_tile_troops(tile)

        return player_id != owner_id or troops != Game.TileTroopMax
