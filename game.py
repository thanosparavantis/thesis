import numpy as np
from sklearn import preprocessing


class Game:
    # The nature player that owns the tiles inbetween the two players
    NaturePlayer = 0

    # The blue player who starts on the upper left corner
    BluePlayer = 1

    # The red player who starts on the lower right corner
    RedPlayer = 2

    # The number of tiles on the x-axis
    MapWidth = 6

    # The number of tiles on the y-axis
    MapHeight = 6

    # The minimum amount of troops for each tile, attack and transfer
    TileTroopMin = 1

    # The maximum amount of troops for each tile, attack and transfer
    TileTroopMax = 32

    # The probability of a soldier spawning in a tile owned by nature
    NatureTroopProbability = 0.1

    # The amount of moves before a player's state is declared stale
    MaxMoves = 10

    InvalidMove = 3
    ProductionMove = 0
    AttackMove = 1
    TransportMove = 2

    def __init__(self):
        # Metadata information about player characteristics
        self._players = None

        # Metadata information about tile owners
        self._map_owners = None

        # Metadata information about troops in tiles
        self._map_troops = None

        # Keeps track of the current player that makes moves on each turn
        self._player_id = None

        # The number of rounds in the game so far
        self._round = None

        # Initializes all variables declared above
        self.reset_game()

        # A min-max scaler that scales inputs to [0, 1] for neural networks
        self._scaler = preprocessing.MinMaxScaler()

    def get_map_owners(self):
        return self._map_owners

    def get_map_troops(self):
        return self._map_troops

    def reset_game(self):
        from game_player import GamePlayer

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
        self._map_owners[1, 1] = Game.BluePlayer
        self._map_owners[Game.MapWidth - 2, Game.MapHeight - 2] = Game.RedPlayer

        self._map_troops = np.zeros_like(self._map_owners)
        self._map_troops[1, 1] = Game.TileTroopMax / 2
        self._map_troops[Game.MapWidth - 2, Game.MapHeight - 2] = Game.TileTroopMax / 2

        self._player_id = Game.BluePlayer
        self.reset_round()

    def change_player_id(self):
        self._player_id = Game.RedPlayer if self._player_id == Game.BluePlayer else Game.BluePlayer

    def get_player_id(self):
        return self._player_id

    def get_player(self, player_id):
        return self._players[player_id]

    def get_round(self):
        return self._round

    def reset_round(self):
        self._round = 1

    def increase_round(self):
        self._round += 1

    def production_move(self, tile_A):
        s_i, s_j = tile_A
        self._map_troops[s_i, s_j] += 1
        player = self._players[self._player_id]
        player.increase_production()

    def is_production_move_valid(self, tile_A):
        my_tiles = self.get_tiles(self._player_id)

        if tile_A not in my_tiles:
            return False

        s_i, s_j = tile_A

        if self._map_troops[s_i, s_j] >= Game.TileTroopMax:
            return False

        return True

    def attack_move(self, tile_A, tile_B, attackers):
        player = self._players[self._player_id]
        s_i, s_j = tile_A
        t_i, t_j = tile_B

        defenders = self._map_troops[t_i, t_j]
        self._map_troops[s_i, s_j] -= attackers

        if defenders < attackers:
            self._map_owners[t_i, t_j] = self._player_id
            player.increase_attacks_succeeded()
        else:
            player.increase_attacks_failed()

        self._map_troops[t_i, t_j] = abs(defenders - attackers)
        player.increase_attacks()

    def is_attack_move_valid(self, tile_A, tile_B, attackers):
        my_tiles = self.get_tiles(self._player_id)
        my_adj_tiles = self.get_tiles_adj(self._player_id)

        if tile_A not in my_tiles:
            return False

        if tile_B not in my_adj_tiles:
            return False

        s_i, s_j = tile_A

        if self._map_troops[s_i, s_j] < attackers:
            return False

        if attackers < Game.TileTroopMin or attackers > Game.TileTroopMax:
            return False

        return True

    def transport_move(self, tile_A, tile_B, transport):
        s_i, s_j = tile_A
        t_i, t_j = tile_B

        self._map_troops[s_i, s_j] -= transport
        self._map_troops[t_i, t_j] += transport

        player = self._players[self._player_id]
        player.increase_transports()

    def is_transport_move_valid(self, tile_A, tile_B, transport):
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

    def get_tile_count(self, player_id):
        return len(self.get_tiles(player_id))

    def get_troop_count(self, player_id):
        troops = 0

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    troops += self._map_troops[i, j]

        return int(troops)

    def get_tiles(self, player_id):
        tiles = []

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    tiles.append((i, j))

        return tiles

    def get_tiles_adj(self, player_id):
        adjacent = set()

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                if self._map_owners[i, j] == player_id:
                    adjacent.add((i - 1, j + 1))
                    adjacent.add((i, j + 1))
                    adjacent.add((i + 1, j + 1))
                    adjacent.add((i - 1, j))
                    adjacent.add((i + 1, j))
                    adjacent.add((i - 1, j - 1))
                    adjacent.add((i, j - 1))
                    adjacent.add((i + 1, j - 1))

        adjacent_valid = set()

        for item in adjacent:
            i, j = item

            if 0 <= i <= Game.MapWidth - 1 and 0 <= j <= Game.MapHeight - 1 and self._map_owners[i, j] != player_id:
                adjacent_valid.add(item)

        return list(adjacent_valid)
