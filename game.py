from typing import Tuple, List

import numpy as np
from numpy import ndarray

from player import Player


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
    IdleMove = -1
    ProductionMove = 0
    AttackMove = 1
    TransportMove = 2
    MaxRounds = 500

    def __init__(self):
        self.players = None
        self.map_owners = None
        self.map_troops = None
        self.player_id = None
        self.rounds = None
        self.states = []
        self.reset_game()

    @staticmethod
    def copy_of(other_game: 'Game') -> 'Game':
        game = Game()
        game.map_owners = other_game.map_owners.copy()
        game.map_troops = other_game.map_troops.copy()
        game.player_id = other_game.player_id
        game.rounds = other_game.rounds
        return game

    def reset_game(self, first_player_id: int = BluePlayer) -> None:
        self.players = [Player('nature', '#CBCBC9'), Player('blue', '#2A8FBD'), Player('red', '#B40406')]
        self.map_owners = np.zeros((Game.MapWidth, Game.MapHeight), dtype='uint8')
        self.map_owners[Game.BlueStartPoint[0], Game.BlueStartPoint[1]] = Game.BluePlayer
        self.map_owners[Game.RedStartPoint[0], Game.RedStartPoint[1]] = Game.RedPlayer
        self.map_troops = np.zeros_like(self.map_owners)
        self.map_troops[Game.BlueStartPoint[0], Game.BlueStartPoint[1]] = Game.StartingTroops
        self.map_troops[Game.RedStartPoint[0], Game.RedStartPoint[1]] = Game.StartingTroops
        self.player_id = first_player_id
        self.states = []
        self.reset_round()

    def create_state(self):
        state = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile = (i, j)
                sign = 1 if self.get_tile_owner(tile) == Game.BluePlayer else -1
                troops = self.get_tile_troops(tile)
                state.append(sign * troops)

        return state

    def save_state(self) -> None:
        self.states.append(self.create_state())

    def is_state_repeated(self) -> bool:
        state = self.create_state()
        repeats = len(list(filter(lambda past_state: past_state == state, self.states))) - 1
        return repeats >= 3

    def get_map_owners(self) -> ndarray:
        return self.map_owners

    def get_map_troops(self) -> ndarray:
        return self.map_troops

    def change_player_id(self) -> None:
        self.player_id = Game.RedPlayer if self.player_id == Game.BluePlayer else Game.BluePlayer

    def get_player_id(self) -> int:
        return self.player_id

    def set_player_id(self, player_id: int) -> None:
        self.player_id = player_id

    def get_enemy_id(self) -> int:
        return Game.BluePlayer if self.player_id == Game.RedPlayer else Game.RedPlayer

    def get_player(self, player_id: int) -> Player:
        return self.players[player_id]

    def get_round(self) -> int:
        return self.rounds

    def reset_round(self) -> None:
        self.rounds = 0

    def increase_round(self) -> None:
        self.rounds += 1

    def production_move(self, source_tile: Tuple[int, int]) -> None:
        s_i, s_j = source_tile
        self.map_troops[s_i, s_j] += 1

    def is_production_move_valid(self, source_tile: Tuple[int, int]) -> bool:
        my_tiles = self.get_tiles(self.player_id)

        if source_tile not in my_tiles:
            return False

        s_i, s_j = source_tile

        if self.map_troops[s_i, s_j] >= Game.TileTroopMax:
            return False

        return True

    def attack_move(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], attackers: int) -> None:
        s_i, s_j = source_tile
        t_i, t_j = target_tile

        self.map_troops[s_i, s_j] -= attackers

        if self.map_troops[s_i, s_j] < Game.TileTroopMin:
            self.map_owners[s_i, s_j] = Game.NaturePlayer

        defenders = self.map_troops[t_i, t_j]

        if defenders < attackers:
            self.map_owners[t_i, t_j] = self.player_id

        self.map_troops[t_i, t_j] = abs(defenders - attackers)

        if self.map_troops[t_i, t_j] < Game.TileTroopMin:
            self.map_owners[t_i, t_j] = Game.NaturePlayer

    def is_attack_move_valid(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], attackers: int) -> bool:
        my_tiles = self.get_tiles(self.player_id)

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

        if self.map_troops[s_i, s_j] < attackers:
            return False

        return True

    def transport_move(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], transport: int) -> None:
        s_i, s_j = source_tile
        t_i, t_j = target_tile

        self.map_troops[s_i, s_j] -= transport

        if self.map_troops[s_i, s_j] < Game.TileTroopMin:
            self.map_owners[s_i, s_j] = Game.NaturePlayer

        self.map_troops[t_i, t_j] += transport

    def is_transport_move_valid(self, source_tile: Tuple[int, int], target_tile: Tuple[int, int], transport: int) -> bool:
        my_tiles = self.get_tiles(self.player_id)

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

        if self.map_troops[s_i, s_j] < transport:
            return False

        if self.map_troops[t_i, t_j] + transport > Game.TileTroopMax:
            return False

        return True

    def get_tile_owner(self, tile: Tuple[int, int]) -> int:
        return self.map_owners[tile[0], tile[1]]

    def get_tile_count(self, player_id: int) -> int:
        return len(self.get_tiles(player_id))

    def get_troop_count(self, player_id: int) -> int:
        tiles = self.get_tiles(player_id)
        return int(np.sum([self.get_tile_troops(tile) for tile in tiles]).item())

    def get_tile_troops(self, tile: Tuple[int, int]) -> int:
        return self.map_troops[tile[0], tile[1]].item()

    @staticmethod
    def get_tile_coords(index: int) -> Tuple[int, int]:
        return [(i, j) for i in range(Game.MapWidth) for j in range(Game.MapHeight)][index]

    def get_tiles(self, player_id: int) -> List[Tuple[int, int]]:
        results = np.argwhere(self.map_owners == player_id)
        return [tuple(result) for result in results]

    @staticmethod
    def get_tile_number(coords: Tuple[int, int]):
        lookup = {
            (0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 3, (0, 4): 4, (0, 5): 5,
            (1, 0): 6, (1, 1): 7, (1, 2): 8, (1, 3): 9, (1, 4): 10, (1, 5): 11,
            (2, 0): 12, (2, 1): 13, (2, 2): 14, (2, 3): 15, (2, 4): 16, (2, 5): 17,
            (3, 0): 18, (3, 1): 19, (3, 2): 20, (3, 3): 21, (3, 4): 22, (3, 5): 23,
            (4, 0): 24, (4, 1): 25, (4, 2): 26, (4, 3): 27, (4, 4): 28, (4, 5): 29,
            (5, 0): 30, (5, 1): 31, (5, 2): 32, (5, 3): 33, (5, 4): 34, (5, 5): 35,
        }

        return lookup[coords]

    @staticmethod
    def get_tile_adj(tile: Tuple[int, int]) -> List[Tuple[int, int]]:
        lookup = {
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

        return lookup[tile]

    def has_ended(self) -> bool:
        blue_tiles = self.get_tile_count(Game.BluePlayer)
        red_tiles = self.get_tile_count(Game.RedPlayer)

        return self.rounds >= Game.MaxRounds or blue_tiles == 0 or red_tiles == 0 or self.is_state_repeated()

    def get_winner(self) -> int:
        blue_tiles = self.get_tile_count(Game.BluePlayer)
        red_tiles = self.get_tile_count(Game.RedPlayer)

        if blue_tiles > 0 and red_tiles == 0:
            return Game.BluePlayer
        elif red_tiles > 0 and blue_tiles == 0:
            return Game.RedPlayer

        return Game.NaturePlayer

    def get_fitness(self):
        return self.get_player_fitness(Game.BluePlayer), self.get_player_fitness(Game.RedPlayer)

    def get_player_fitness(self, player_id: int) -> float:
        player = self.get_player(player_id)
        tile_count = self.get_tile_count(player_id)
        troop_count = self.get_troop_count(player_id)

        return ((tile_count / Game.MapSize) * 70) + ((troop_count / (Game.MapSize * Game.TileTroopMax)) * 30)
