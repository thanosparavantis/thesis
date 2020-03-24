class GamePlayer:
    def __init__(self, name, tile_color, tile_alpha):
        self._tile_name = name
        self._tile_color = tile_color
        self._tile_alpha = tile_alpha
        self._total_production = 0
        self._total_attacks = 0
        self._total_attacks_succeeded = 0
        self._total_attacks_failed = 0
        self._total_transports = 0

    def get_tile_name(self):
        return self._tile_name

    def get_tile_color(self):
        return self._tile_color

    def get_tile_alpha(self):
        return self._tile_alpha

    def get_total_production(self):
        return self._total_production

    def get_total_attacks(self):
        return self._total_attacks

    def get_total_attacks_suceeded(self):
        return self._total_attacks_succeeded

    def get_total_attacks_failed(self):
        return self._total_attacks_failed

    def get_total_transports(self):
        return self._total_transports

    def increase_production(self):
        self._total_production += 1

    def increase_attacks(self):
        self._total_attacks += 1

    def increase_attacks_succeeded(self):
        self._total_attacks_succeeded += 1

    def increase_attacks_failed(self):
        self._total_attacks_failed += 1

    def increase_transports(self):
        self._total_transports += 1
