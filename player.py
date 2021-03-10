class Player:
    def __init__(self, name: str, tile_color: str) -> None:
        self.tile_name = name
        self.tile_color = tile_color
        self.move_history = []
        self.tile_history = [1]
        self.troop_history = [1]
