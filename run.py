import glob
import os
from collections import defaultdict
from sys import stdout
from typing import List, Tuple, Dict

import neat
from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, StdOutReporter, StatisticsReporter, Checkpointer, Population
from neat.nn import FeedForwardNetwork
from numpy import ndarray

import GameStats
from Game import Game
from GameMap import GameMap
from GameStats import GameStatistics
from GenomeGraph import GenomeGraph
from StateParser import StateParser

from visualize import draw_net


def main():
    print('=' * 50)
    print('Thesis Project')
    print('=' * 50)
    print('* Athanasios Paravantis')
    print('* P16112')
    print('* thanosparavantis@gmail.com')
    print('=' * 50)
    print()

    game = Game()
    state_parser = StateParser(game)
    game_map = GameMap(game, state_parser)
    game_stats = GameStatistics(game)
    genome_graph = GenomeGraph(game, state_parser)

    neat_config = neat.Config(
        DefaultGenome,
        DefaultReproduction,
        DefaultSpeciesSet,
        DefaultStagnation,
        './config'
    )

    if not os.path.isdir('./checkpoints'):
        os.mkdir('./checkpoints')

    # game_stats.render()
    # game_map.render()

    blue_pop = pop_setup('blue', neat_config)
    red_pop = pop_setup('red', neat_config)

    for iteration in range(1, 101):
        blue_fitness, red_fitness = evaluate_fitness(
            blue_pop.population,
            red_pop.population,
            neat_config,
            state_parser,
            game,
            game_map,
            game_stats,
        )

        blue_genome = blue_pop.run(lambda genomes, config: assign_fitness(genomes, blue_fitness), 1)
        red_genome = red_pop.run(lambda genomes, config: assign_fitness(genomes, red_fitness), 1)

        # draw_net(neat_config, blue_genome, filename='graphs/blue_genome', fmt='png')
        # draw_net(neat_config, red_genome, filename='graphs/red_genome', fmt='png')
        #
        # game_stats.add_blue_fitness(blue_genome.fitness)
        # game_stats.add_red_fitness(red_genome.fitness)
        # game_stats.render()
        #
        # if iterations > 0 and iterations % 10 == 0:
        #     play_game(blue_genome, red_genome, neat_config, state_parser, game, game_map, True)


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


def evaluate_fitness(blue_genomes: Dict[int, neat.DefaultGenome], red_genomes: Dict[int, neat.DefaultGenome], config: neat.Config, state_parser: StateParser, game: Game, game_map: GameMap, game_stats: GameStats) -> Tuple[Dict[int, float], Dict[int, float]]:
    blue_fitness_dict = defaultdict(list)
    red_fitness_dict = defaultdict(list)

    iteration = 1

    for blue_id, blue_genome in blue_genomes.items():
        for red_id, red_genome in red_genomes.items():

            play_game(blue_genome, red_genome, config, state_parser, game, game_map, False)

            blue_fitness, red_fitness = game.get_fitness()

            # print(f'{iteration}. Playing Blue {blue_id} against Red {red_id}')

            blue_fitness_dict[blue_id].append(blue_fitness)
            red_fitness_dict[red_id].append(red_fitness)

            iteration += 1

    blue_fitness_best = dict()
    red_fitness_best = dict()

    for blue_id, fitness_per_game in blue_fitness_dict.items():
        blue_fitness_best[blue_id] = max(fitness_per_game)

    for red_id, fitness_per_game in red_fitness_dict.items():
        red_fitness_best[red_id] = max(fitness_per_game)

    return blue_fitness_best, red_fitness_best


def assign_fitness(genomes: List[Tuple[int, neat.DefaultGenome]], fitness_mapping: Dict[int, float]) -> None:
    for genome_id, genome in genomes:
        genome.fitness = fitness_mapping[genome.key]


def play_game(blue_genome: neat.DefaultGenome, red_genome: neat.DefaultGenome, config: neat.Config, state_parser: StateParser, game: Game, game_map: GameMap, render: bool = False) -> None:
    game.reset_game()
    game_map.set_genomes(blue_genome, red_genome)

    if render:
        game_map.render()

    blue_nn = FeedForwardNetwork.create(blue_genome, config)
    red_nn = FeedForwardNetwork.create(red_genome, config)

    while True:
        game.set_player_id(Game.BluePlayer)
        blue_move, blue_added_fitness = play_move(blue_nn, red_nn, state_parser, game, game_map, render)
        game.set_blue_added_fitness(blue_added_fitness)
        blue_move_type = blue_move['move_type']

        if game.has_ended():
            if render:
                game_map.render()
            break

        game.set_player_id(Game.RedPlayer)
        red_move, red_added_fitness = play_move(blue_nn, red_nn, state_parser, game, game_map, render)
        game.set_red_added_fitness(red_added_fitness)
        red_move_type = red_move['move_type']

        if game.has_ended():
            if render:
                game_map.render()
            break

        if blue_move_type == Game.IdleMove and red_move_type == Game.IdleMove:
            break

        game.increase_round()


def play_move(blue_nn: neat.nn.FeedForwardNetwork, red_nn: neat.nn.FeedForwardNetwork, state_parser: StateParser, game: Game, game_map: GameMap, render: bool = False) -> (Dict, float):
    player_id = game.get_player_id()
    network = blue_nn if player_id == Game.BluePlayer else red_nn
    network_output = network.activate(state_parser.encode_state())
    player_move, added_fitness = state_parser.decode_state(network_output)

    move_type = player_move['move_type']
    source_tile = player_move['source_tile']
    target_tile = player_move['target_tile']
    troops = player_move['troops']

    if move_type == Game.ProductionMove:
        game.production_move(source_tile)
    elif move_type == Game.AttackMove:
        game.attack_move(source_tile, target_tile, troops)
    elif move_type == Game.TransportMove:
        game.transport_move(source_tile, target_tile, troops)

    game_map.set_player_move(player_move)

    if render:
        game_map.render()

    return player_move, added_fitness


if __name__ == '__main__':
    main()
