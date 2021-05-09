from typing import Tuple

import numpy as np
from numpy import ndarray

from game import Game


class GamePresetOne(Game):
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
        start_tiles = 6
        start_troops = 40
        current_tiles = self.get_tile_count(Game.RedPlayer)
        current_troops = self.get_troop_count(Game.RedPlayer)
        game_won = 25 if self.get_winner() == Game.BluePlayer else 0
        time_bonus = ((abs(self.rounds - Game.MaxRounds) / Game.MaxRounds) * 25) if self.get_winner() == Game.BluePlayer else 0
        tile_progress = ((start_tiles - current_tiles) / start_tiles) * 25
        troop_progress = ((start_troops - current_troops) / start_troops) * 25

        return game_won + time_bonus + tile_progress + troop_progress


class GamePresetTwo(Game):
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

    def get_fitness(self) -> float:
        start_tiles = 19
        start_troops = 222
        current_tiles = self.get_tile_count(Game.RedPlayer)
        current_troops = self.get_troop_count(Game.RedPlayer)
        game_won = 25 if self.get_winner() == Game.BluePlayer else 0
        time_bonus = ((abs(self.rounds - Game.MaxRounds) / Game.MaxRounds) * 25) if self.get_winner() == Game.BluePlayer else 0
        tile_progress = ((start_tiles - current_tiles) / start_tiles) * 25
        troop_progress = ((start_troops - current_troops) / start_troops) * 25

        return game_won + time_bonus + tile_progress + troop_progress
