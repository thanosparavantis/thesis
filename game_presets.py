from typing import Tuple

import numpy as np
from numpy import ndarray

from game import Game


class BlueBeatRedEasy(Game):
    def __init__(self):
        super().__init__()

    def get_map(self) -> Tuple[ndarray, ndarray]:
        map_owners = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 2, 0, 2, 2, 0],
            [0, 2, 2, 0, 2, 0],
            [0, 0, 0, 0, 0, 0],
        ])

        map_troops = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 10, 0, 5, 5, 0],
            [0, 5, 5, 0, 10, 0],
            [0, 0, 0, 0, 0, 0],
        ])

        return map_owners, map_troops

    def get_fitness(self) -> float:
        enemy_start_tiles = 6
        enemy_start_troops = 40
        enemy_tiles = self.get_tile_count(Game.RedPlayer)
        enemy_troops = self.get_troop_count(Game.RedPlayer)

        game_won = 20 if self.get_winner() == Game.BluePlayer else 0
        game_won_time = ((abs(self.rounds - self.get_max_rounds()) / self.get_max_rounds()) * 30) if self.get_winner() == Game.BluePlayer else 0

        enemy_tiles_lost = ((enemy_start_tiles - enemy_tiles) / enemy_start_tiles) * 30
        enemy_troops_lost = ((enemy_start_troops - enemy_troops) / enemy_start_troops) * 20

        return sum([
            game_won, game_won_time,
            enemy_tiles_lost, enemy_troops_lost
        ])

    def is_red_simulated(self) -> bool:
        return False


class BlueBeatRedHard(Game):
    def __init__(self):
        super().__init__()

    def get_map(self) -> Tuple[ndarray, ndarray]:
        map_owners = np.zeros((Game.MapWidth, Game.MapHeight), dtype='uint8')
        map_troops = np.zeros((Game.MapWidth, Game.MapHeight), dtype='uint8')

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if i == 0 and j == 0:
                    map_owners[i, j] = Game.BluePlayer
                    map_troops[i, j] = Game.TileTroopMin
                else:
                    map_owners[i, j] = self.random.choice([Game.NaturePlayer, Game.RedPlayer])

                    if map_owners[i, j] != Game.NaturePlayer:
                        map_troops[i, j] = self.random.integers(1, 21)

        return map_owners, map_troops

    def get_max_rounds(self) -> int:
        return 5000

    def get_fitness(self) -> float:
        enemy_start_tiles = 19
        enemy_start_troops = 222
        enemy_tiles = self.get_tile_count(Game.RedPlayer)
        enemy_troops = self.get_troop_count(Game.RedPlayer)

        game_won = 20 if self.get_winner() == Game.BluePlayer else 0
        game_won_time = ((abs(self.rounds - self.get_max_rounds()) / self.get_max_rounds()) * 30) if self.get_winner() == Game.BluePlayer else 0
        enemy_tiles_lost = ((enemy_start_tiles - enemy_tiles) / enemy_start_tiles) * 30
        enemy_troops_lost = ((enemy_start_troops - enemy_troops) / enemy_start_troops) * 20

        return sum([
            game_won, game_won_time,
            enemy_tiles_lost, enemy_troops_lost
        ])

    def is_red_simulated(self) -> bool:
        return False


class BlueExpandAlone(Game):
    def __init__(self):
        super().__init__()

    def get_map(self) -> Tuple[ndarray, ndarray]:
        map_owners = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ])

        map_troops = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ])

        return map_owners, map_troops

    def get_max_rounds(self) -> int:
        return 5000

    def get_fitness(self) -> float:
        nature_start_tiles = 36
        nature_tiles = self.get_tile_count(Game.NaturePlayer)

        game_won = 20 if self.get_winner() == Game.BluePlayer else 0
        game_won_time = ((abs(self.rounds - self.get_max_rounds()) / self.get_max_rounds()) * 30) if self.get_winner() == Game.BluePlayer else 0
        my_tiles_gained = ((nature_start_tiles - nature_tiles) / nature_start_tiles) * 50

        return sum([
            game_won, game_won_time, my_tiles_gained
        ])

    def is_red_simulated(self) -> bool:
        return False

    def has_ended(self) -> bool:
        return self.rounds >= self.get_max_rounds() \
               or self.get_tile_count(Game.NaturePlayer) == 0 \
               or self.is_state_repeated()

    def get_winner(self) -> int:
        if self.get_tile_count(Game.NaturePlayer) == 0:
            return Game.BluePlayer
        else:
            return Game.NaturePlayer


class BlueAgainstRed(Game):
    def get_fitness(self) -> float:
        enemy_tiles = self.get_tile_count(Game.RedPlayer)
        enemy_troops = self.get_troop_count(Game.RedPlayer)

        game_won = 20 if self.get_winner() == Game.BluePlayer else 0
        game_won_time = ((abs(self.rounds - self.get_max_rounds()) / self.get_max_rounds()) * 30) if self.get_winner() == Game.BluePlayer else 0
        enemy_tiles_lost = 30 - ((enemy_tiles / Game.MapSize) * 30)
        enemy_troops_lost = 20 - ((enemy_troops / (Game.MapSize * Game.TileTroopMax)) * 20)

        return sum([
            game_won, game_won_time,
            enemy_tiles_lost, enemy_troops_lost
        ])
