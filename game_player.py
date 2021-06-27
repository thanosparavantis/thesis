class GamePlayer:
    def __init__(self, name: str, tile_color: str) -> None:
        self.tile_name = name
        self.tile_color = tile_color
        self.production_moves = 0
        self.attack_moves = 0
        self.transport_moves = 0
        self.per_move_fitness = []
