from neat import DefaultGenome

from game import Game


class GameResult:
    def __init__(self, genome: DefaultGenome = None, game: Game = None, game_json: dict = None):
        if game_json:
            self.genome_key = game_json['genome_key']
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
            self.blue_guided_moves = game_json['blue_guided_moves'] if 'blue_guided_moves' in game_json else 0
            self.red_guided_moves = game_json['red_guided_moves'] if 'red_guided_moves' in game_json else 0
            self.fitness = game_json['fitness']
            self.winner = game_json['winner']
        else:
            self.genome_key = genome.key
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
            self.fitness = game.get_fitness()

            winner_id = game.get_winner()

            if winner_id == Game.BluePlayer:
                self.winner = 'Blue'
            elif winner_id == Game.RedPlayer:
                self.winner = 'Red'
            else:
                self.winner = 'Tie'

    def __str__(self):
        return f'Genome: {self.genome_key:>5}' \
               f'{"":4}' \
               f'Rounds: {self.rounds:>4}' \
               f'{"":4}' \
               f'Tiles: {self.blue_tiles:>2} / {self.red_tiles:<2}' \
               f'{"":4}' \
               f'Troops: {self.blue_troops:>3} / {self.red_troops:>3}' \
               f'{"":4}' \
               f'Fitness: {self.fitness:>7.3f}' \
               f'{"":4}' \
               f'Winner: {self.winner:>4}'
