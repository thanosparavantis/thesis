import glob
import os
from typing import List

import neat
from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, StdOutReporter, \
    StatisticsReporter, Checkpointer, Population
from neat.nn import FeedForwardNetwork

import GameStats
from Game import Game
from GameMap import GameMap
from GameStats import GameStatistics
from NeuralNetworkParser import NeuralNetworkParser


def main():
    game = Game()
    game_map = GameMap(game)
    game_stats = GameStatistics()
    nn_parser = NeuralNetworkParser(game)

    neat_config = neat.Config(
        DefaultGenome,
        DefaultReproduction,
        DefaultSpeciesSet,
        DefaultStagnation,
        './config'
    )

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
    pop.add_reporter(Checkpointer(
        generation_interval=1,
        filename_prefix='./checkpoints/neat-checkpoint-'))

    while True:
        genome = pop.run(
            lambda genomes, config:
            evaluate_fitness(genomes, config, nn_parser, game, game_map, game_stats),
            1
        )

        play_game(genome, neat_config, nn_parser, game, game_map, True)


def evaluate_fitness(genomes: List[neat.DefaultGenome],
                     config: neat.Config,
                     nn_parser: NeuralNetworkParser,
                     game: Game,
                     game_map: GameMap,
                     game_stats: GameStats):
    for genome_id, genome in genomes:
        genome.fitness = 0

        play_game(genome, config, nn_parser, game, game_map, False)

        genome.fitness = game.get_tile_count(Game.BluePlayer) + game.get_tile_count(Game.RedPlayer) + game.get_round()

        record_stats(genome, game, game_stats)
        game.reset_game()


def record_stats(genome: neat.DefaultGenome,
                 game: Game,
                 game_stats: GameStats):
    blue_player = game.get_player(Game.BluePlayer)
    red_player = game.get_player(Game.RedPlayer)

    game_stats.add_fitness(genome.fitness)
    game_stats.add_blue_production(blue_player.get_total_production())
    game_stats.add_red_production(red_player.get_total_production())
    game_stats.add_blue_attack(blue_player.get_total_attacks())
    game_stats.add_red_attack(red_player.get_total_attacks())
    game_stats.add_blue_transport(blue_player.get_total_transports())
    game_stats.add_red_transport(red_player.get_total_transports())
    game_stats.render_plot()


def play_game(genome: neat.DefaultGenome,
              config: neat.Config,
              nn_parser: NeuralNetworkParser,
              game: Game,
              game_map: GameMap,
              render: bool = False):
    network = FeedForwardNetwork.create(genome, config)

    if render:
        game_map.render(
            f'Overview',
            f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome.key}     Fitness: {genome.fitness}'
        )

    while True:
        player_move = make_move(genome, network, nn_parser, game, game_map, render)

        if player_move["move_type"] == Game.InvalidMove or game.get_tile_count(game.get_player_id()) == 0:
            break

        game.change_player_id()

        player_move = make_move(genome, network, nn_parser, game, game_map, render)

        if player_move["move_type"] == Game.InvalidMove or game.get_tile_count(game.get_player_id()) == 0:
            break

        game.change_player_id()

        game.increase_round()


def make_move(genome: neat.DefaultGenome,
              network: neat.nn.FeedForwardNetwork,
              nn_parser: NeuralNetworkParser,
              game: Game,
              game_map: GameMap,
              render: bool = False):
    network_output = network.activate(nn_parser.encode_state())
    player_move = nn_parser.decode_state(network_output)

    move_type = player_move["move_type"]
    tile_A = player_move["tile_A"]
    tile_B = player_move["tile_B"]
    troops = player_move["troops"]

    move = 'Invalid Move'

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
        game_map.render(
            f'{move}',
            f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome.key}     Fitness: {genome.fitness}'
        )

        print(player_move)

    return player_move


if __name__ == '__main__':
    main()
