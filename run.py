import glob
import os

import neat
from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, StdOutReporter, StatisticsReporter, Checkpointer, Population
from neat.nn import FeedForwardNetwork

from game_map import GameMap
from nn_parser import NeuralNetworkParser


def get_fitness(genomes, config):
    total_production_blue = 0
    total_production_red = 0
    total_attacks_blue = 0
    total_attacks_red = 0
    total_transports_blue = 0
    total_transports_red = 0

    for genome_id, genome in genomes:
        play_game(genome, config, calc_fitness=True, render=False)

        blue_player = game.get_player(Game.BluePlayer)
        red_player = game.get_player(Game.RedPlayer)
        total_production_blue += blue_player.get_total_production()
        total_production_red += red_player.get_total_production()
        total_attacks_blue += blue_player.get_total_attacks()
        total_attacks_red += red_player.get_total_attacks()
        total_transports_blue += blue_player.get_total_transports()
        total_transports_red += red_player.get_total_transports()

        game.reset_game()

    game_stats.add_blue_production(total_production_blue)
    game_stats.add_red_production(total_production_red)
    game_stats.add_blue_attack(total_attacks_blue)
    game_stats.add_red_attack(total_attacks_red)
    game_stats.add_blue_transport(total_transports_blue)
    game_stats.add_red_transport(total_transports_red)


def play_game(genome, config, calc_fitness=False, render=False):
    while True:
        player_move = make_move(genome, config, render)

        if player_move["move_type"] == Game.InvalidMove or game.get_tiles(game.get_player_id()) == 0:
            break

        game.change_player_id()

        player_move = make_move(genome, config, render)

        if player_move["move_type"] == Game.InvalidMove or game.get_tiles(game.get_player_id()) == 0:
            break

        game.change_player_id()

        game.increase_round()

    if calc_fitness:
        genome.fitness = (game.get_player(Game.BluePlayer).get_total_attacks() + game.get_player(Game.RedPlayer).get_total_attacks()) ** 2


def make_move(genome, config, render=False):
    network = FeedForwardNetwork.create(genome, config)
    network_output = network.activate(nn_parser.encode_state())
    player_move = nn_parser.decode_output(network_output)

    move_type = player_move["move_type"]
    tile_A = player_move["tile_A"]
    tile_B = player_move["tile_B"]
    troops = player_move["troops"]

    move = 'Waiting...'

    if render:
        game_map.render(
            f'{move}',
            f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome.key}     Fitness: {genome.fitness}'
        )

    if move_type == Game.ProductionMove:
        game.production_move(tile_A)
        move = f'Production Move {tile_A}'
    elif move_type == Game.AttackMove:
        game.attack_move(tile_A, tile_B, troops)
        move = f'Attack Move {tile_A} → {tile_B} with {troops} troops'
    elif move_type == Game.TransportMove:
        game.transport_move(tile_A, tile_B, troops)
        move = f'Transport Move {tile_A} → {tile_B} with {troops} troops'

    if render:
        print(game.get_round(), game.get_player_id(), player_move)
        game_map.render(
            f'{move}',
            f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome.key}     Fitness: {genome.fitness}'
        )

    return player_move


if __name__ == '__main__':
    from game import Game
    from game_stats import GameStatistics

    game = Game()
    game_map = GameMap(game)
    game_stats = GameStatistics()
    nn_parser = NeuralNetworkParser(game)

    neat_config = neat.Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    if not os.path.isdir('./checkpoints'):
        os.mkdir('./checkpoints')

    ckp_list = glob.glob('./checkpoints/*')

    if len(ckp_list) > 0:
        ckp_file = max(ckp_list, key=os.path.getctime)
        print(f'Loading checkpoint: {ckp_file}')
        pop = Checkpointer.restore_checkpoint(ckp_file)
    else:
        print('Creating new population')
        pop = Population(neat_config)

    pop.add_reporter(StdOutReporter(True))
    pop.add_reporter(StatisticsReporter())
    pop.add_reporter(Checkpointer(10, filename_prefix='./checkpoints/neat-checkpoint-'))

    last_genome = None

    while True:
        chosen_genome = pop.run(get_fitness, 1)

        game_stats.add_fitness(chosen_genome.fitness)
        game_stats.render_plot()

        if last_genome == chosen_genome:
            continue
        else:
            last_genome = chosen_genome

        play_game(chosen_genome, neat_config, calc_fitness=False, render=True)
