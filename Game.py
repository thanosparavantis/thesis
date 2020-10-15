from typing import Tuple, List

import numpy as np
from numpy import ndarray
from sklearn import preprocessing

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
    InvalidMove = -1
    ProductionMove = 0
    AttackMove = 1
    TransportMove = 2
    AbandonTile = False

    def __init__(self):
        self._players = None
        self._map_owners = None
        self._map_troops = None
        self._player_id = None
        self._round = None
        self.reset_game()
        self._scaler = preprocessing.MinMaxScaler()

    def get_map_owners(self) -> ndarray:
        return self._map_owners

    def get_map_troops(self) -> ndarray:
        return self._map_troops

    def reset_game(self) -> None:
        from GamePlayer import GamePlayer

        self._players = [
            GamePlayer(name='nature',
                       tile_color='#CBCBC9',
                       tile_alpha=0.2),

            GamePlayer(name='blue',
                       tile_color='#2A8FBD',
                       tile_alpha=0.5),

            GamePlayer(name='red',
                       tile_color='#B40406',
                       tile_alpha=0.5),
        ]

        self._map_owners = np.zeros((Game.MapWidth, Game.MapHeight), dtype='uint8')
        self._map_owners[Game.BlueStartPoint[0], Game.BlueStartPoint[1]] = Game.BluePlayer
        self._map_owners[Game.RedStartPoint[0], Game.RedStartPoint[1]] = Game.RedPlayer
        self._map_troops = np.zeros_like(self._map_owners)
        self._map_troops[Game.BlueStartPoint[0], Game.BlueStartPoint[1]] = Game.StartingTroops
        self._map_troops[Game.RedStartPoint[0], Game.RedStartPoint[1]] = Game.StartingTroops
        self._player_id = Game.BluePlayer
        self.reset_round()

    def change_player_id(self) -> None:
        self._player_id = Game.RedPlayer if self._player_id == Game.BluePlayer else Game.BluePlayer

    def get_player_id(self) -> int:
        return self._player_id

    def get_player(self, player_id: int) -> GamePlayer:
        return self._players[player_id]

    def get_round(self) -> int:
        return self._round

    def reset_round(self) -> None:
        self._round = 1

    def increase_round(self) -> None:
        self._round += 1

    def production_move(self, tile_A: Tuple[int, int]) -> None:
        s_i, s_j = tile_A
        self._map_troops[s_i, s_j] += 1
        player = self._players[self._player_id]
        player.increase_production()

    def is_production_move_valid(self, tile_A: Tuple[int, int]) -> bool:
        my_tiles = self.get_tiles(self._player_id)

        if tile_A not in my_tiles:
            return False

        s_i, s_j = tile_A

        if self._map_troops[s_i, s_j] >= Game.TileTroopMax:
            return False

        return True

    def attack_move(self, tile_A: Tuple[int, int], tile_B: Tuple[int, int], attackers: int) -> None:
        player = self._players[self._player_id]
        s_i, s_j = tile_A
        t_i, t_j = tile_B

        self._map_troops[s_i, s_j] -= attackers
        defenders = self._map_troops[t_i, t_j]

        if defenders < attackers:
            self._map_owners[t_i, t_j] = self._player_id
            player.increase_attacks_succeeded()
        else:
            player.increase_attacks_failed()

        self._map_troops[t_i, t_j] = abs(defenders - attackers)
        player.increase_attacks()

    def is_attack_move_valid(self, tile_A: Tuple[int, int], tile_B: Tuple[int, int], attackers: int) -> bool:
        my_tiles = self.get_tiles(self._player_id)
        my_adj_tiles = self.get_global_tiles_adj(self._player_id)

        if tile_A not in my_tiles:
            return False

        if tile_B not in my_adj_tiles:
            return False

        s_i, s_j = tile_A

        if attackers < Game.TileTroopMin or attackers > Game.TileTroopMax:
            return False

        if self._map_troops[s_i, s_j] < attackers:
            return False

        return True

    def transport_move(self, tile_A: Tuple[int, int], tile_B: Tuple[int, int], transport: int) -> None:
        s_i, s_j = tile_A
        t_i, t_j = tile_B

        self._map_troops[s_i, s_j] -= transport
        self._map_troops[t_i, t_j] += transport

        player = self._players[self._player_id]
        player.increase_transports()

    def is_transport_move_valid(self, tile_A: Tuple[int, int], tile_B: Tuple[int, int], transport: int) -> bool:
        my_tiles = self.get_tiles(self._player_id)

        if tile_A not in my_tiles:
            return False

        if tile_B not in my_tiles:
            return False

        if tile_A == tile_B:
            return False

        s_i, s_j = tile_A
        t_i, t_j = tile_B

        if abs(s_i - t_i) > 1 or abs(s_j - t_j) > 1:
            return False

        if transport < Game.TileTroopMin or transport > Game.TileTroopMax:
            return False

        if self._map_troops[s_i, s_j] < transport:
            return False

        if self._map_troops[t_i, t_j] + transport > Game.TileTroopMax:
            return False

        return True

    def get_tile_count(self, player_id: int) -> int:
        return len(self.get_tiles(player_id))

    def get_troop_count(self, player_id: int) -> int:
        troops = 0

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    troops += self._map_troops[i, j]

        return int(troops)

    def get_tile_troops(self, tile: Tuple[int, int]) -> int:
        return self._map_troops[tile[0], tile[1]]

    @staticmethod
    def get_tile_coords(index: int) -> Tuple[int, int]:
        return [(i, j) for i in range(Game.MapWidth) for j in range(Game.MapHeight)][index]

    def get_tiles(self, player_id: int) -> List[Tuple[int, int]]:
        tiles = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    tiles.append((i, j))

        return tiles

    def get_global_tiles_adj(self, player_id: int) -> List[Tuple[int, int]]:
        adjacent_options = set()

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    adjacent_options.add((i - 1, j + 1))
                    adjacent_options.add((i, j + 1))
                    adjacent_options.add((i + 1, j + 1))
                    adjacent_options.add((i - 1, j))
                    adjacent_options.add((i + 1, j))
                    adjacent_options.add((i - 1, j - 1))
                    adjacent_options.add((i, j - 1))
                    adjacent_options.add((i + 1, j - 1))

        adjacent_tiles = set()

        for item in adjacent_options:
            i, j = item
            if 0 <= i <= Game.MapWidth - 1 and 0 <= j <= Game.MapHeight - 1 and self._map_owners[i, j] != player_id:
                adjacent_tiles.add(item)

        return list(adjacent_tiles)

    def get_tiles_adj(self, tile: Tuple[int, int]) -> List[Tuple[int, int]]:
        adjacent_options = [
            (tile[0] - 1, tile[1] - 1),
            (tile[0] - 1, tile[1]),
            (tile[0] - 1, tile[1] + 1),
            (tile[0], tile[1] - 1),
            (tile[0], tile[1] + 1),
            (tile[0] + 1, tile[1] + 1),
            (tile[0] + 1, tile[1]),
            (tile[0] + 1, tile[1] - 1)
        ]

        adjacent_tiles = []

        for tile in adjacent_options:
            i, j = tile
            if 0 <= i <= Game.MapWidth - 1 and 0 <= j <= Game.MapHeight - 1:
                adjacent_tiles.append(tile)

        return adjacent_tiles
