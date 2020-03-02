class Player:
    CursorA = 0
    CursorB = 1

    def __init__(self, name, cursor_a, cursor_b, tile_color, tile_alpha):
        self._tile_name = name
        self._tile_color = tile_color
        self._tile_alpha = tile_alpha
        self._total_production = 0
        self._total_attacks = 0
        self._total_attacks_succeeded = 0
        self._total_attacks_failed = 0
        self._total_transports = 0
        self._cursor_a = cursor_a
        self._cursor_b = cursor_b

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

    def _eval_cursor(self, cursor_type):
        return self._cursor_a if cursor_type == self.CursorA else self._cursor_b

    def get_cursor(self, cursor_type):
        return tuple(self._eval_cursor(cursor_type))

    def move_up(self, cursor_type):
        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        cursor[0] = i + 1

    def can_move_up(self, cursor_type):
        from game import Game

        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        return i + 1 < Game.MapWidth

    def move_down(self, cursor_type):
        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        cursor[0] = i - 1

    def can_move_down(self, cursor_type):
        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        return i - 1 > 0

    def move_left(self, cursor_type):
        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        cursor[1] = j - 1

    def can_move_left(self, cursor_type):
        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        return j - 1 > 0

    def move_right(self, cursor_type):
        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        cursor[1] = j + 1

    def can_move_right(self, cursor_type):
        from game import Game

        cursor = self._eval_cursor(cursor_type)
        i, j = cursor

        return j + 1 < Game.MapHeight
