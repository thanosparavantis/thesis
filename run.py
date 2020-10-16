import asyncio
import glob
import math
import os
from collections import defaultdict
from typing import List, Tuple, Dict

import neat
from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, StdOutReporter, \
    StatisticsReporter, Checkpointer, Population
from neat.nn import FeedForwardNetwork

import GameStats
from Game import Game
from GameMap import GameMap
from GameStats import GameStatistics
from NeuralNetworkParser import NeuralNetworkParser


async def main():
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

    # game_stats.render_plot()

    blue_pop = pop_setup('blue', neat_config)
    red_pop = pop_setup('red', neat_config)

    while True:
        blue_fitness, red_fitness = evaluate_fitness(
            blue_pop.population,
            red_pop.population,
            neat_config,
            nn_parser,
            game,
            game_map,
            game_stats
        )

        blue_genome = blue_pop.run(lambda genomes, config: assign_fitness(genomes, blue_fitness), 1)
        red_genome = red_pop.run(lambda genomes, config: assign_fitness(genomes, red_fitness), 1)

        print('=' * 50)
        print('Playing most fit game')
        print('=' * 50)

        # play_game(blue_genome, red_genome, neat_config, nn_parser, game, game_map, True)


def pop_setup(name, neat_config):
    if not os.path.isdir(f'./checkpoints/{name}'):
        os.mkdir(f'./checkpoints/{name}')

    ckp_list = glob.glob(f'./checkpoints/{name}/*')

    if len(ckp_list) > 0:
        ckp_file = max(ckp_list, key=os.path.getctime)
        print(f'Loading {name} checkpoint: {ckp_file}')
        pop = Checkpointer.restore_checkpoint(ckp_file)
    else:
        print(f'Creating new population for {name}')
        pop = Population(neat_config)

    pop.add_reporter(StdOutReporter(True))
    pop.add_reporter(StatisticsReporter())
    pop.add_reporter(Checkpointer(generation_interval=1, filename_prefix=f'./checkpoints/{name}/neat-checkpoint-'))

    return pop


def evaluate_fitness(blue_genomes: Dict[int, neat.DefaultGenome],
                     red_genomes: Dict[int, neat.DefaultGenome],
                     config: neat.Config,
                     nn_parser: NeuralNetworkParser,
                     game: Game,
                     game_map: GameMap,
                     game_stats: GameStats) -> Tuple[Dict[int, float], Dict[int, float]]:
    blue_fitness = defaultdict(list)
    red_fitness = defaultdict(list)

    for blue_id, blue_genome in blue_genomes.items():
        for red_id, red_genome in red_genomes.items():
            print(f'Training Blue {blue_id} against Red {red_id}')
            play_game(blue_genome, red_genome, config, nn_parser, game, game_map, False)

            blue_fitness_score = (game.get_tile_count(Game.BluePlayer) - game.get_tile_count(Game.RedPlayer)) + (game.get_tile_count(Game.BluePlayer) - game.get_tile_count(Game.NaturePlayer))
            red_fitness_score = game.get_tile_count(Game.RedPlayer) - game.get_tile_count(Game.BluePlayer) + (game.get_tile_count(Game.RedPlayer) - game.get_tile_count(Game.NaturePlayer))
            blue_fitness[blue_id].append(blue_fitness_score)
            red_fitness[red_id].append(red_fitness_score)

            blue_player = game.get_player(Game.BluePlayer)
            red_player = game.get_player(Game.RedPlayer)

            # game_stats.add_blue_fitness(blue_fitness_score)
            # game_stats.add_red_fitness(red_fitness_score)
            # game_stats.add_blue_production(blue_player.get_total_production())
            # game_stats.add_red_production(red_player.get_total_production())
            # game_stats.add_blue_attack(blue_player.get_total_attacks())
            # game_stats.add_red_attack(red_player.get_total_attacks())
            # game_stats.add_blue_transport(blue_player.get_total_transports())
            # game_stats.add_red_transport(red_player.get_total_transports())

            game.reset_game()
            # game_stats.render_plot()

    blue_fitness_best = dict()
    red_fitness_best = dict()

    for blue_id, fitness_per_game in blue_fitness.items():
        blue_fitness_best[blue_id] = max(fitness_per_game)

    for red_id, fitness_per_game in red_fitness.items():
        red_fitness_best[red_id] = max(fitness_per_game)

    return blue_fitness_best, red_fitness_best


def assign_fitness(genomes: List[Tuple[int, neat.DefaultGenome]], fitness_mapping: Dict[int, float]) -> None:
    for genome_id, genome in genomes:
        genome.fitness = fitness_mapping[genome.key]


def play_game(blue_genome: neat.DefaultGenome,
              red_genome: neat.DefaultGenome,
              config: neat.Config,
              nn_parser: NeuralNetworkParser,
              game: Game,
              game_map: GameMap,
              render: bool = False):
    blue_nn = FeedForwardNetwork.create(blue_genome, config)
    red_nn = FeedForwardNetwork.create(red_genome, config)

    if render:
        render_map('Overview', game, game_map, blue_genome, red_genome)

    while True:
        if game.get_tile_count(game.get_player_id()) == 0:
            if render:
                render_map('END', game, game_map, blue_genome, red_genome)
            break

        make_move(blue_genome, red_genome, blue_nn, red_nn, nn_parser, game, game_map, render)

        game.change_player_id()

        if game.get_tile_count(game.get_player_id()) == 0:
            if render:
                render_map('END', game, game_map, blue_genome, red_genome)
            break

        make_move(blue_genome, red_genome, blue_nn, red_nn, nn_parser, game, game_map, render)

        game.change_player_id()

        game.increase_round()

        if game.get_round() >= (game.get_tile_count(Game.BluePlayer) + game.get_tile_count(Game.RedPlayer)) * 10:
            break


def make_move(blue_genome: neat.DefaultGenome,
              red_genome: neat.DefaultGenome,
              blue_nn: neat.nn.FeedForwardNetwork,
              red_nn: neat.nn.FeedForwardNetwork,
              nn_parser: NeuralNetworkParser,
              game: Game,
              game_map: GameMap,
              render: bool = False):
    network = blue_nn if game.get_player_id() == Game.BluePlayer else red_nn
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
        render_map(move, game, game_map, blue_genome, red_genome)
        print(f'{game.get_round()}.{game.get_player_id()} {move}')

    return player_move


def render_map(title, game, game_map, blue_genome, red_genome):
    round = game.get_round()
    player_id = game.get_player_id()
    blue_id = blue_genome.key
    red_id = red_genome.key
    blue_fitness = blue_genome.fitness if blue_genome.fitness is not None else 0
    red_fitness = red_genome.fitness if red_genome.fitness is not None else 0

    game_map.render(
        title,
        f'Round: {round}.{player_id}     Genomes: {blue_id}/{red_id}     Fitness: {blue_fitness}/{red_fitness}'
    )


if __name__ == '__main__':
    asyncio.run(main())
