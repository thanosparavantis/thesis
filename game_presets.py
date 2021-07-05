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

    def get_max_rounds(self) -> int:
        return 500

    def get_fitness(self) -> float:
        enemy_start_tiles = 6
        enemy_start_troops = 40
        enemy_tiles = self.get_tile_count(Game.RedPlayer)
        enemy_troops = self.get_troop_count(Game.RedPlayer)
        blue_won = self.get_winner() == Game.BluePlayer

        game_won_time = (
                ((abs(self.rounds - self.get_max_rounds()) / self.get_max_rounds()) ** 2) * 50) if blue_won else 0
        enemy_tiles_lost = (((enemy_start_tiles - enemy_tiles) / enemy_start_tiles) ** 2) * 30
        enemy_troops_lost = (((enemy_start_troops - enemy_troops) / enemy_start_troops) ** 2) * 20

        return sum([game_won_time, enemy_tiles_lost, enemy_troops_lost])

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
        blue_won = self.get_winner() == Game.BluePlayer

        game_won_time = (
                ((abs(self.rounds - self.get_max_rounds()) / self.get_max_rounds()) ** 2) * 50) if blue_won else 0
        enemy_tiles_lost = (((enemy_start_tiles - enemy_tiles) / enemy_start_tiles) ** 2) * 30
        enemy_troops_lost = (((enemy_start_troops - enemy_troops) / enemy_start_troops) ** 2) * 20

        return sum([game_won_time, enemy_tiles_lost, enemy_troops_lost])

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
        blue_fit = sum(self.blue_player.per_move_fitness)
        return blue_fit

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
    def get_max_rounds(self) -> int:
        return 500

    def get_fitness(self) -> float:
        player = self.get_player(Game.BluePlayer)

        if len(player.per_move_fitness) > 0:
            return sum(player.per_move_fitness) / len(player.per_move_fitness)
        else:
            return 0.0
