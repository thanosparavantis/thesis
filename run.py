import glob
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
from GenomeGraph import GenomeGraph
from StateParser import StateParser


def main():
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

    game_stats.render()
    game_map.render()

    blue_pop = pop_setup('blue', neat_config)
    red_pop = pop_setup('red', neat_config)

    iterations = 1

    while True:
        blue_fitness, red_fitness = evaluate_fitness(
            blue_pop.population,
            red_pop.population,
            neat_config,
            state_parser,
            game,
            game_map,
            game_stats,
            genome_graph
        )

        blue_genome = blue_pop.run(lambda genomes, config: assign_fitness(genomes, blue_fitness), 1)
        red_genome = red_pop.run(lambda genomes, config: assign_fitness(genomes, red_fitness), 1)

        if iterations % 10 == 0:
            play_game(blue_genome, red_genome, neat_config, state_parser, game, game_map, genome_graph, True)
        else:
            play_game(blue_genome, red_genome, neat_config, state_parser, game, game_map, genome_graph, False)
            game_map.render()

        game_stats.add_blue_fitness(blue_genome.fitness)
        game_stats.add_red_fitness(red_genome.fitness)
        game_stats.render()

        game.reset_game()
        iterations += 1


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


def evaluate_fitness(blue_genomes: Dict[int, neat.DefaultGenome], red_genomes: Dict[int, neat.DefaultGenome], config: neat.Config, state_parser: StateParser, game: Game, game_map: GameMap, game_stats: GameStats, genome_graph: GenomeGraph) -> Tuple[Dict[int, float], Dict[int, float]]:
    blue_fitness_max = 0
    red_fitness_max = 0
    blue_fitness_dict = defaultdict(list)
    red_fitness_dict = defaultdict(list)

    for blue_id, blue_genome in blue_genomes.items():
        for red_id, red_genome in red_genomes.items():
            play_game(blue_genome, red_genome, config, state_parser, game, game_map, genome_graph, False)

            blue_fitness, red_fitness = game.get_fitness()
            winner = game.get_winner()

            if winner == Game.BluePlayer:
                status = 'Blue Won'
            elif winner == Game.RedPlayer:
                status = 'Red Won'
            else:
                status = 'Tie'

            fitness_record = ''

            if blue_fitness > blue_fitness_max:
                blue_fitness_max = blue_fitness
                fitness_record = f'Blue highscore ({blue_fitness})'
            elif red_fitness > red_fitness_max:
                red_fitness_max = red_fitness
                fitness_record = f'Red highscore ({red_fitness})'
            elif blue_fitness > blue_fitness_max and red_fitness > red_fitness_max:
                blue_fitness_max = blue_fitness
                red_fitness_max = red_fitness
                fitness_record = f'New highscore ({blue_fitness}/{red_fitness})'

            rounds = game.get_round()

            print(f'Genomes: {blue_id:^5}/{red_id:^5} Fitness: {blue_fitness:^8.4}/{red_fitness:^8.4} Rounds: {rounds:^6} Status: {status:<10} {fitness_record}')

            blue_fitness_dict[blue_id].append(blue_fitness)
            red_fitness_dict[red_id].append(red_fitness)

            game_map.render()
            game.reset_game()

    blue_fitness_best = dict()
    red_fitness_best = dict()

    for blue_id, fitness_per_game in blue_fitness_dict.items():
        blue_fitness = max(fitness_per_game)
        blue_fitness_best[blue_id] = blue_fitness

    for red_id, fitness_per_game in red_fitness_dict.items():
        red_fitness = max(fitness_per_game)
        red_fitness_best[red_id] = red_fitness

    return blue_fitness_best, red_fitness_best


def assign_fitness(genomes: List[Tuple[int, neat.DefaultGenome]], fitness_mapping: Dict[int, float]) -> None:
    for genome_id, genome in genomes:
        genome.fitness = fitness_mapping[genome.key]


def play_game(blue_genome: neat.DefaultGenome, red_genome: neat.DefaultGenome, config: neat.Config, state_parser: StateParser, game: Game, game_map: GameMap, genome_graph: GenomeGraph, render: bool = False) -> None:
    blue_nn = FeedForwardNetwork.create(blue_genome, config)
    red_nn = FeedForwardNetwork.create(red_genome, config)

    game_map.set_genomes(blue_genome, red_genome)

    if render:
        game_map.render()

    while True:
        player_move = play_move(blue_nn, red_nn, state_parser, game, game_map, render)

        if game.has_ended() or player_move['move_type'] == Game.InvalidMove:
            if render:
                game_map.render()

            break

        game.change_player_id()

        player_move = play_move(blue_nn, red_nn, state_parser, game, game_map, render)

        if game.has_ended() or player_move['move_type'] == Game.InvalidMove:
            if render:
                game_map.render()

            break

        game.change_player_id()

        game.increase_round()


def play_move(blue_nn: neat.nn.FeedForwardNetwork, red_nn: neat.nn.FeedForwardNetwork, state_parser: StateParser, game: Game, game_map: GameMap, render: bool = False) -> Dict:
    player_id = game.get_player_id()
    network = blue_nn if player_id == Game.BluePlayer else red_nn
    network_output = network.activate(state_parser.encode_state())
    player_move = state_parser.decode_state(network_output)

    move_type = player_move['move_type']
    tile_A = player_move['tile_A']
    tile_B = player_move['tile_B']
    troops = player_move['troops']

    if move_type == Game.ProductionMove:
        game.production_move(tile_A)
    elif move_type == Game.AttackMove:
        game.attack_move(tile_A, tile_B, troops)
    elif move_type == Game.TransportMove:
        game.transport_move(tile_A, tile_B, troops)
    else:
        print(player_move)

    game_map.set_player_move(player_move)

    if render:
        game_map.render()

    return player_move


if __name__ == '__main__':
    main()
