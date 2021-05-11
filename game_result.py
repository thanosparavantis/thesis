import inspect

from neat import DefaultGenome
from pushbullet import Pushbullet

from game import Game


class GameResult:
    pb = Pushbullet(api_key='o.Ni4QO9yfo4vKFNeSrlNMFxYfdsiB5CaP')

    def __init__(self, genome: DefaultGenome = None, game: Game = None, game_json: dict = None):
        if game_json:
            self.genome_key = game_json['genome_key'] if 'genome_key' in game_json else 0
            self.rounds = game_json['rounds'] if 'rounds' in game_json else 0
            self.blue_tiles = game_json['blue_tiles'] if 'blue_tiles' in game_json else 0
            self.red_tiles = game_json['red_tiles'] if 'red_tiles' in game_json else 0
            self.blue_troops = game_json['blue_troops'] if 'blue_troops' in game_json else 0
            self.red_troops = game_json['red_troops'] if 'red_troops' in game_json else 0
            self.blue_production_moves = game_json[
                'blue_production_moves'] if 'blue_production_moves' in game_json else 0
            self.red_production_moves = game_json['red_production_moves'] if 'red_production_moves' in game_json else 0
            self.blue_attack_moves = game_json['blue_attack_moves'] if 'blue_attack_moves' in game_json else 0
            self.red_attack_moves = game_json['red_attack_moves'] if 'red_attack_moves' in game_json else 0
            self.blue_transport_moves = game_json['blue_transport_moves'] if 'blue_transport_moves' in game_json else 0
            self.red_transport_moves = game_json['red_transport_moves'] if 'red_transport_moves' in game_json else 0
            self.fitness = game_json['fitness'] if 'fitness' in game_json else 0.0
            self.winner = game_json['winner'] if 'winner' in game_json else 'Tie'
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
            self.fitness = game.get_fitness()

            winner_id = game.get_winner()

            if winner_id == Game.BluePlayer:
                self.winner = 'Blue'
            elif winner_id == Game.RedPlayer:
                self.winner = 'Red'
            else:
                self.winner = 'Tie'

    def notify_pushbullet(self):
        self.pb.push_note(
            title=f'Generation TEST',
            body=inspect.cleandoc(f"""
                Genome: {self.genome_key}
                Fitness: {self.fitness:>.4f}
                Blue Tiles: {self.blue_tiles}
                Red Tiles: {self.red_tiles}
                Blue Troops: {self.blue_troops}
                Red Troops: {self.red_troops}
                Winner: {self.winner}
            """))

    def __str__(self):
        return f'Genome: {self.genome_key:>4}' \
               f'{"":2}' \
               f'Rounds: {self.rounds:>4}' \
               f'{"":2}' \
               f'Tiles: {self.blue_tiles:>2} / {self.red_tiles:<2}' \
               f'{"":2}' \
               f'Troops: {self.blue_troops:>3} / {self.red_troops:>3}' \
               f'{"":2}' \
               f'Fitness: {self.fitness:>6.1f}' \
               f'{"":2}' \
               f'Winner: {self.winner:>4}'
