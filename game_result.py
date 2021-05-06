from neat import DefaultGenome

from game import Game


class GameResult:
    def __init__(self, blue_genome: DefaultGenome = None, red_genome: DefaultGenome = None, game: Game = None, game_json: dict = None):
        if game_json:
            self.blue_key = game_json['blue_key']
            self.red_key = game_json['red_key']
            self.rounds = game_json['rounds']
            self.blue_tiles = game_json['blue_tiles']
            self.red_tiles = game_json['red_tiles']
            self.blue_troops = game_json['blue_troops']
            self.red_troops = game_json['red_troops']
            self.blue_fitness = game_json['blue_fitness']
            self.red_fitness = game_json['red_fitness']
            self.winner = game_json['winner']
        else:
            self.blue_key = blue_genome.key
            self.red_key = red_genome.key
            self.rounds = game.rounds
            self.blue_tiles = game.get_tile_count(Game.BluePlayer)
            self.red_tiles = game.get_tile_count(Game.RedPlayer)
            self.blue_troops = game.get_troop_count(Game.BluePlayer)
            self.red_troops = game.get_troop_count(Game.RedPlayer)
            self.blue_fitness, self.red_fitness = game.get_fitness()

            winner_id = game.get_winner()

            if winner_id == Game.BluePlayer:
                self.winner = 'Blue'
            elif winner_id == Game.RedPlayer:
                self.winner = 'Red'
            else:
                self.winner = 'Tie'

    def __str__(self):
        return f'Genome: {self.blue_key:>4} / {self.red_key:<4}' \
               f'{"":2}' \
               f'Rounds: {self.rounds:>4}' \
               f'{"":2}' \
               f'Tiles: {self.blue_tiles:>2} / {self.red_tiles:<2}' \
               f'{"":2}' \
               f'Troops: {self.blue_troops:>3} / {self.red_troops:>3}' \
               f'{"":2}' \
               f'Fitness: {self.blue_fitness:>6.1f} / {self.red_fitness:<6.1f}' \
               f'{"":2}' \
               f'Winner: {self.winner:>4}'
