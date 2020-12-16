import glob
import os
from collections import defaultdict
from typing import Dict, Tuple, List

from neat import Checkpointer, Population, StdOutReporter, StatisticsReporter, DefaultGenome, Config
from neat.nn import FeedForwardNetwork

from game import Game
from game_map import GameMap
from state_parser import StateParser


def print_signature():
    print('=' * 50)
    print('Thesis Project')
    print('=' * 50)
    print('* Athanasios Paravantis')
    print('* P16112')
    print('* thanosparavantis@gmail.com')
    print('=' * 50)
    print()


def pop_setup(
        name,
        neat_config
) -> Population:
    if not os.path.isdir('./checkpoints'):
        os.mkdir('./checkpoints')

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


def evaluate_fitness(
        blue_genomes: Dict[int, DefaultGenome],
        red_genomes: Dict[int, DefaultGenome],
        config: Config,
        state_parser: StateParser,
        game: Game,
        game_map: GameMap
) -> Tuple[Dict[int, float], Dict[int, float]]:
    blue_fitness_dict = defaultdict(list)
    red_fitness_dict = defaultdict(list)

    iteration = 1

    for blue_id, blue_genome in blue_genomes.items():
        for red_id, red_genome in red_genomes.items():
            play_game(blue_genome, red_genome, config, state_parser, game, game_map, False)

            blue_fitness, red_fitness = game.get_fitness()

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


def assign_fitness(
        genomes: List[Tuple[int, DefaultGenome]],
        fitness_mapping: Dict[int, float]
) -> None:
    for genome_id, genome in genomes:
        genome.fitness = fitness_mapping[genome.key]


def play_game(
        blue_genome: DefaultGenome,
        red_genome: DefaultGenome,
        config: Config,
        state_parser: StateParser,
        game: Game,
        game_map: GameMap,
        render: bool = False
) -> None:
    game.reset_game()
    game_map.set_genomes(blue_genome, red_genome)

    if render:
        game_map.render()

    blue_net = FeedForwardNetwork.create(blue_genome, config)
    red_net = FeedForwardNetwork.create(red_genome, config)

    while True:
        game.set_player_id(Game.BluePlayer)
        blue_move = play_move(blue_net, red_net, state_parser, game, game_map, render)

        if game.has_ended():
            if render:
                game_map.render()
            break

        game.set_player_id(Game.RedPlayer)
        red_move = play_move(blue_net, red_net, state_parser, game, game_map, render)

        if game.has_ended():
            if render:
                game_map.render()
            break

        game.increase_round()


def play_move(
        blue_net: FeedForwardNetwork,
        red_net: FeedForwardNetwork,
        state_parser: StateParser,
        game: Game,
        game_map: GameMap,
        render: bool = False
) -> Dict:
    player_id = game.get_player_id()
    net = blue_net if player_id == Game.BluePlayer else red_net
    net_out = net.activate(state_parser.encode_state())
    player_move = state_parser.decode_state(net_out)

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

    return player_move
