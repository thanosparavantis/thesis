from typing import Tuple, List

import numpy as np
from numpy import ndarray

from GamePlayer import GamePlayer


class Game:
    MapWidth = 6
    MapHeight = 6
    MapSize = MapWidth * MapHeight
    NaturePlayer = 0
    BluePlayer = 1
    BlueStartPoint = (0, 0)
    RedPlayer = 2
    RedStartPoint = (MapWidth - 1, MapHeight - 1)
    TileTroopMin = 1
    TileTroopMax = 20
    StartingTroops = TileTroopMin
    NatureTroopProbability = 0.1
    IdleMove = -1
    ProductionMove = 0
    AttackMove = 1
    TransportMove = 2
    MaxRounds = 500

    def __init__(self):
        self._players = None
        self._map_owners = None
        self._map_troops = None
        self._player_id = None
        self._round = None
        self._blue_added_fitness = 0
        self._red_added_fitness = 0
        self.reset_game()

    @staticmethod
    def copy_of(other_game: 'Game') -> 'Game':
        game = Game()
        game._map_owners = other_game._map_owners.copy()
        game._map_troops = other_game._map_troops.copy()
        game._player_id = other_game._player_id
        game._round = other_game._round
        return game

    def get_map_owners(self) -> ndarray:
        return self._map_owners

    def get_map_troops(self) -> ndarray:
        return self._map_troops

    def reset_game(self, first_player_id: int = BluePlayer) -> None:
        self._players = [GamePlayer('nature', '#CBCBC9'), GamePlayer('blue', '#2A8FBD'), GamePlayer('red', '#B40406')]
        self._map_owners = np.zeros((Game.MapWidth, Game.MapHeight), dtype='uint8')
        self._map_owners[Game.BlueStartPoint[0], Game.BlueStartPoint[1]] = Game.BluePlayer
        self._map_owners[Game.RedStartPoint[0], Game.RedStartPoint[1]] = Game.RedPlayer
        self._map_troops = np.zeros_like(self._map_owners)
        self._map_troops[Game.BlueStartPoint[0], Game.BlueStartPoint[1]] = Game.StartingTroops
        self._map_troops[Game.RedStartPoint[0], Game.RedStartPoint[1]] = Game.StartingTroops
        self._player_id = first_player_id
        self._blue_added_fitness = 0
        self._red_added_fitness = 0
        self.reset_round()

    def change_player_id(self) -> None:
        self._player_id = Game.RedPlayer if self._player_id == Game.BluePlayer else Game.BluePlayer

    def get_player_id(self) -> int:
        return self._player_id

    def set_player_id(self, player_id: int) -> None:
        self._player_id = player_id

    def get_enemy_id(self) -> int:
        return Game.BluePlayer if self._player_id == Game.RedPlayer else Game.RedPlayer

    def get_player(self, player_id: int) -> GamePlayer:
        return self._players[player_id]

    def get_round(self) -> int:
        return self._round

    def reset_round(self) -> None:
        self._round = 1

    def increase_round(self) -> None:
        self._round += 1

    def set_blue_added_fitness(self, added_fitness: int) -> None:
        self._blue_added_fitness = added_fitness

    def set_red_added_fitness(self, added_fitness: int) -> None:
        self._red_added_fitness = added_fitness

    def production_move(self, source_tile: Tuple[int, int]) -> None:
        s_i, s_j = source_tile
        self._map_troops[s_i, s_j] += 1
        player = self._players[self._player_id]
        player.increase_production()

    def is_production_move_valid(self, source_tile: Tuple[int, int]) -> bool:
        my_tiles = self.get_tiles(self._player_id)

        if source_tile not in my_tiles:
            return False

        s_i, s_j = source_tile

        if self._map_troops[s_i, s_j] >= Game.TileTroopMax:
            return False

        return True

    def attack_move(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], attackers: int) -> None:
        player = self._players[self._player_id]
        s_i, s_j = source_tile
        t_i, t_j = target_tile

        self._map_troops[s_i, s_j] -= attackers

        if self._map_troops[s_i, s_j] < Game.TileTroopMin:
            self._map_owners[s_i, s_j] = Game.NaturePlayer

        defenders = self._map_troops[t_i, t_j]

        if defenders < attackers:
            self._map_owners[t_i, t_j] = self._player_id

            if self._map_troops[s_i, s_j] >= Game.TileTroopMin:
                player.increase_attacks_succeeded()
        else:
            player.increase_attacks_failed()

        self._map_troops[t_i, t_j] = abs(defenders - attackers)

        if self._map_troops[t_i, t_j] < Game.TileTroopMin:
            self._map_owners[t_i, t_j] = Game.NaturePlayer

        player.increase_attacks()

    def is_attack_move_valid(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], attackers: int) -> bool:
        my_tiles = self.get_tiles(self._player_id)

        if source_tile not in my_tiles:
            return False

        if target_tile in my_tiles:
            return False

        adjacent = self.get_tile_adj(source_tile)

        if target_tile not in adjacent:
            return False

        s_i, s_j = source_tile

        if attackers < Game.TileTroopMin or attackers > Game.TileTroopMax:
            return False

        if self._map_troops[s_i, s_j] < attackers:
            return False

        return True

    def transport_move(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], transport: int) -> None:
        s_i, s_j = source_tile
        t_i, t_j = target_tile

        self._map_troops[s_i, s_j] -= transport

        if self._map_troops[s_i, s_j] < Game.TileTroopMin:
            self._map_owners[s_i, s_j] = Game.NaturePlayer

        self._map_troops[t_i, t_j] += transport

        player = self._players[self._player_id]
        player.increase_transports()

    def is_transport_move_valid(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], transport: int) -> bool:
        my_tiles = self.get_tiles(self._player_id)

        if source_tile not in my_tiles:
            return False

        if target_tile not in my_tiles:
            return False

        if source_tile == target_tile:
            return False

        s_i, s_j = source_tile
        t_i, t_j = target_tile

        if abs(s_i - t_i) > 1 or abs(s_j - t_j) > 1:
            return False

        if transport < Game.TileTroopMin or transport > Game.TileTroopMax:
            return False

        if self._map_troops[s_i, s_j] < transport:
            return False

        if self._map_troops[t_i, t_j] + transport > Game.TileTroopMax:
            return False

        return True

    def get_tile_owner(self, tile: Tuple[int, int]) -> int:
        return self._map_owners[tile[0], tile[1]]

    def get_tile_count(self, player_id: int) -> int:
        return len(self.get_tiles(player_id))

    def get_troop_count(self, player_id: int) -> int:
        tiles = self.get_tiles(player_id)
        return np.sum([self.get_tile_troops(tile) for tile in tiles]).item()

    def get_tile_troops(self, tile: Tuple[int, int]) -> int:
        return self._map_troops[tile[0], tile[1]].item()

    @staticmethod
    def get_tile_coords(index: int) -> Tuple[int, int]:
        return [(i, j) for i in range(Game.MapWidth) for j in range(Game.MapHeight)][index]

    def get_tiles(self, player_id: int) -> List[Tuple[int, int]]:
        results = np.argwhere(self._map_owners == player_id)
        return [tuple(result) for result in results]

    @staticmethod
    def get_tile_adj(tile: Tuple[int, int]) -> List[Tuple[int, int]]:
        adjacent_options = {
            (0, 0): [(0, 1), (1, 0)],
            (0, 1): [(0, 0), (0, 2), (1, 0), (1, 1)],
            (0, 2): [(0, 1), (1, 1), (1, 2), (0, 3)],
            (0, 3): [(0, 2), (1, 2), (1, 3), (0, 4)],
            (0, 4): [(0, 3), (1, 3), (1, 4), (0, 5)],
            (0, 5): [(0, 4), (1, 4), (1, 5)],
            (1, 0): [(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)],
            (1, 1): [(0, 1), (0, 2), (1, 0), (1, 2), (2, 1), (2, 2)],
            (1, 2): [(0, 2), (0, 3), (1, 1), (1, 3), (2, 2), (2, 3)],
            (1, 3): [(0, 3), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4)],
            (1, 4): [(0, 4), (0, 5), (1, 3), (1, 5), (2, 4), (2, 5)],
            (1, 5): [(0, 5), (1, 4), (2, 5)],
            (2, 0): [(1, 0), (2, 1), (3, 0)],
            (2, 1): [(1, 0), (1, 1), (2, 0), (2, 2), (3, 0), (3, 1)],
            (2, 2): [(1, 1), (1, 2), (2, 1), (2, 3), (3, 1), (3, 2)],
            (2, 3): [(1, 2), (1, 3), (2, 2), (2, 4), (3, 2), (3, 3)],
            (2, 4): [(1, 3), (1, 4), (2, 3), (2, 5), (3, 3), (3, 4)],
            (2, 5): [(1, 4), (1, 5), (2, 4), (3, 4), (3, 5)],
            (3, 0): [(2, 0), (2, 1), (3, 1), (4, 0), (4, 1)],
            (3, 1): [(2, 1), (2, 2), (3, 0), (3, 2), (4, 1), (4, 2)],
            (3, 2): [(2, 2), (2, 3), (3, 1), (3, 3), (4, 2), (4, 3)],
            (3, 3): [(2, 3), (2, 4), (3, 2), (3, 4), (4, 3), (4, 4)],
            (3, 4): [(2, 4), (2, 5), (3, 3), (3, 5), (4, 4), (4, 5)],
            (3, 5): [(2, 5), (3, 4), (4, 5)],
            (4, 0): [(3, 0), (4, 1), (5, 0)],
            (4, 1): [(3, 0), (3, 1), (4, 0), (4, 2), (5, 0), (5, 1)],
            (4, 2): [(3, 1), (3, 2), (4, 1), (4, 3), (5, 1), (5, 2)],
            (4, 3): [(3, 2), (3, 3), (4, 2), (4, 4), (5, 2), (5, 3)],
            (4, 4): [(3, 3), (3, 4), (4, 3), (4, 5), (5, 3), (5, 4)],
            (4, 5): [(3, 4), (3, 5), (4, 4), (5, 4), (5, 5)],
            (5, 0): [(4, 0), (4, 1), (5, 1)],
            (5, 1): [(4, 1), (4, 2), (5, 0), (5, 2)],
            (5, 2): [(4, 2), (4, 3), (5, 1), (5, 3)],
            (5, 3): [(4, 3), (4, 4), (5, 2), (5, 4)],
            (5, 4): [(4, 4), (4, 5), (5, 3), (5, 5)],
            (5, 5): [(4, 5), (5, 4)],
        }

        return adjacent_options[tile]

    def has_ended(self) -> bool:
        blue_tiles = self.get_tile_count(Game.BluePlayer)
        red_tiles = self.get_tile_count(Game.RedPlayer)

        return self._round >= Game.MaxRounds or blue_tiles == 0 or red_tiles == 0

    def get_winner(self) -> int:
        blue_tiles = self.get_tile_count(Game.BluePlayer)
        red_tiles = self.get_tile_count(Game.RedPlayer)

        if blue_tiles > 0 and red_tiles == 0:
            return Game.BluePlayer
        elif red_tiles > 0 and blue_tiles == 0:
            return Game.RedPlayer

        return Game.NaturePlayer

    def get_fitness(self):
        blue_tiles = self.get_tiles(Game.BluePlayer)
        blue_tile_count = len(blue_tiles)
        blue_troop_count = self.get_troop_count(Game.BluePlayer)
        red_tiles = self.get_tiles(Game.RedPlayer)
        red_tile_count = len(red_tiles)
        red_troop_count = self.get_troop_count(Game.RedPlayer)
        max_tile_count = Game.MapSize
        max_troop_count = Game.TileTroopMax * Game.MapSize
        blue_player = self.get_player(Game.BluePlayer)
        red_player = self.get_player(Game.RedPlayer)

        blue_fitness = 0
        red_fitness = 0

        # blue_fitness = blue_player.get_total_attacks_succeeded()
        blue_fitness += blue_tile_count - max_tile_count
        blue_fitness += blue_troop_count - max_troop_count
        # blue_fitness += 1.0 * (blue_tile_count / max_tile_count)
        # blue_fitness += 0.3 * (blue_troop_count / max_troop_count)
        # blue_fitness += self._blue_added_fitness
        # blue_fitness += blue_player.get_total_production()
        # blue_fitness += blue_player.get_total_attacks()
        # blue_fitness += blue_player.get_total_transports()

        # red_fitness = red_player.get_total_attacks_succeeded()
        red_fitness += red_tile_count - max_tile_count
        red_fitness += red_troop_count - max_troop_count
        # red_fitness += 1.0 * (red_tile_count / max_tile_count)
        # red_fitness += 0.3 * (red_troop_count / max_troop_count)
        # red_fitness += self._red_added_fitness
        # red_fitness += red_player.get_total_production()
        # red_fitness += red_player.get_total_attacks()
        # red_fitness += red_player.get_total_transports()

        return float(blue_fitness), float(red_fitness)
