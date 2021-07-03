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
            self.blue_production_moves = game_json['blue_production_moves']
            self.red_production_moves = game_json['red_production_moves']
            self.blue_attack_moves = game_json['blue_attack_moves']
            self.red_attack_moves = game_json['red_attack_moves']
            self.blue_transport_moves = game_json['blue_transport_moves']
            self.red_transport_moves = game_json['red_transport_moves']
            self.blue_guided_moves = game_json['blue_guided_moves']
            self.red_guided_moves = game_json['red_guided_moves']
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
            self.blue_production_moves = game.blue_player.production_moves
            self.red_production_moves = game.red_player.production_moves
            self.blue_attack_moves = game.blue_player.attack_moves
            self.red_attack_moves = game.red_player.attack_moves
            self.blue_transport_moves = game.blue_player.transport_moves
            self.red_transport_moves = game.red_player.transport_moves
            self.blue_guided_moves = game.blue_player.guided_moves
            self.red_guided_moves = game.red_player.guided_moves
            self.blue_fitness, self.red_fitness = game.get_fitness()

            winner_id = game.get_winner()

            if winner_id == Game.BluePlayer:
                self.winner = 'Blue'
            elif winner_id == Game.RedPlayer:
                self.winner = 'Red'
            else:
                self.winner = 'Tie'

    def __str__(self):
        return f'Genome: {self.blue_key:>4} / {self.red_key:>4}' \
               f'{"":4}' \
               f'Rounds: {self.rounds:>3}' \
               f'{"":4}' \
               f'Tiles: {self.blue_tiles:>2} / {self.red_tiles:>2}' \
               f'{"":4}' \
               f'Troops: {self.blue_troops:>3} / {self.red_troops:>3}' \
               f'{"":4}' \
               f'Fitness: {self.blue_fitness:>7.3f} / {self.red_fitness:>7.3f}' \
               f'{"":4}' \
               f'Winner: {self.winner:>4}'
