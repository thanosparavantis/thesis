from typing import List, Dict


class Player:
    def __init__(self, name: str, tile_color: str) -> None:
        self._tile_name = name
        self._tile_color = tile_color
        self._moves = []
        self._award = 0
        self._penalty = 0

    def get_tile_name(self) -> str:
        return self._tile_name

    def get_tile_color(self) -> str:
        return self._tile_color

    def add_move(self, move: Dict) -> None:
        self._moves.append(move)

    def get_moves(self) -> List[Dict]:
        return self._moves

    def award(self) -> None:
        self._award += 1

    def get_award(self) -> int:
        return self._award

    def penalize(self, amount: int = 1) -> None:
        self._penalty += amount

    def get_penalty(self) -> int:
        return self._penalty
