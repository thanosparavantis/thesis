import os.path
import pickle
import random
from typing import Tuple

from game import Game


class ZobristHashing:
    KeysFilename = 'zobrist_keys'
    DataFilename = 'zobrist_data'

    def __init__(self):
        self._keys = dict()
        self._data = dict()

        if os.path.isfile(ZobristHashing.KeysFilename):
            self._load_keys()
        else:
            self._create_keys()
            self._save_keys()

        if os.path.isfile(ZobristHashing.DataFilename):
            self._load_data()
        else:
            self.save_data()

    def _create_keys(self):
        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile = (i, j)
                self._keys[self._get_lookup_key(tile, Game.NaturePlayer, 0)] = self._random()

                for troops in range(1, Game.TileTroopMax + 1):
                    self._keys[self._get_lookup_key(tile, Game.BluePlayer, troops)] = self._random()
                    self._keys[self._get_lookup_key(tile, Game.RedPlayer, troops)] = self._random()

    def _load_keys(self):
        file = open(ZobristHashing.KeysFilename, 'rb')
        self._keys = pickle.load(file)
        file.close()

    def _save_keys(self):
        file = open(ZobristHashing.KeysFilename, 'wb')
        pickle.dump(self._keys, file)
        file.close()

    def _load_data(self):
        file = open(ZobristHashing.DataFilename, 'rb')
        self._data = pickle.load(file)
        file.close()
        print(f'Loaded data: {len(self._data)}')

    def save_data(self):
        print('Saving data')
        file = open(ZobristHashing.DataFilename, 'wb')
        pickle.dump(self._data, file)
        file.close()

    def _get_lookup_key(self, tile: Tuple[int, int], owner_id, troops) -> str:
        return f'{tile[0]}{tile[1]}{owner_id}{troops}'

    def _get_key(self, tile: Tuple[int, int], owner_id, troops) -> int:
        return self._keys[self._get_lookup_key(tile, owner_id, troops)]

    @staticmethod
    def _random() -> int:
        return random.getrandbits(64)

    def get_game_hash(self, game: Game) -> int:
        values = []
        game_hash = 0

        for i in range(Game.MapWidth):
            for j in range(Game.MapHeight):
                tile = (i, j)
                owner_id = game.get_tile_owner(tile)
                troops = game.get_tile_troops(tile)
                values.append(self._get_key((i, j), owner_id, troops))

        for value in values:
            game_hash ^= value

        return game_hash

    def update_game_hash(self, game: Game, move: dict, game_hash: int) -> int:
        tile_source = move['tile_source']
        tile_source_owner_id = game.get_tile_owner(tile_source)
        tile_source_troops = game.get_tile_troops(tile_source)
        game_hash ^= self._get_key(tile_source, tile_source_owner_id, tile_source_troops)

        tile_target = move['tile_target']

        if tile_target is not None:
            tile_target_owner_id = game.get_tile_owner(tile_target)
            tile_target_troops = game.get_tile_troops(tile_target)
            game_hash ^= self._get_key(tile_target, tile_target_owner_id, tile_target_troops)

        return game_hash

    def get_data(self, game_hash: int) -> int:
        return self._data[game_hash]

    def has_data(self, game_hash: int):
        return game_hash in self._data

    def store_data(self, game_hash: int, evaluation: int) -> None:
        self._data[game_hash] = evaluation
