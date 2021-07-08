import argparse
import json
import os
import re
from argparse import Namespace
from multiprocessing import Pool, Lock, Manager, Value
from multiprocessing.queues import Queue
from typing import Dict, Tuple, List

from neat import Checkpointer, Population, StdOutReporter, StatisticsReporter, DefaultGenome, Config
from neat.nn import FeedForwardNetwork

from game import Game
from game_map import GameMap
from game_presets import BlueBeatRedEasy, BlueBeatRedHard, BlueExpandAlone, BlueAgainstRed
from game_result import GameResult


def print_signature(title):
    print('=' * 50)
    print(f'  {title}')
    print('=' * 50)
    print('* Athanasios Paravantis')
    print('* thanosparavantis@gmail.com')
    print('=' * 50)
    print()


def parse_args(description) -> Namespace:
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '-p',
        '--preset',
        dest='preset',
        metavar='ID',
        type=int,
        help='the preferred game preset to use for training',
        required=True
    )

    args = parser.parse_args()

    print(f'Selected game preset: {args.preset}')

    return args


def game_setup(preset: int) -> Game:
    if preset == 1:
        return BlueBeatRedEasy()
    elif preset == 2:
        return BlueBeatRedHard()
    elif preset == 3:
        return BlueExpandAlone()
    elif preset == 4:
        return BlueAgainstRed()
    else:
        return Game()


def get_folder_contents(path) -> List[str]:
    files = os.listdir(path)
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    files = sorted(files, key=alphanum_key)
    return files


def pop_setup(neat_config: Config, preset: int, ckp_number: int = None) -> Population:
    folder = f'./checkpoints-{preset}'
    filename = f'checkpoint-{ckp_number}'

    if ckp_number:
        ckp_file = f'{folder}/{filename}'
        pop = Checkpointer.restore_checkpoint(ckp_file)
        print(f'Loaded predefined checkpoint: {ckp_file}')
    else:

        if not os.path.isdir(folder):
            os.mkdir(folder)

        ckp_list = get_folder_contents(f'{folder}')

        if len(ckp_list) > 0:
            ckp_file = f'{folder}/{ckp_list[-1]}'
            pop = Checkpointer.restore_checkpoint(ckp_file)
            print(f'Loaded checkpoint: {ckp_file}')
        else:
            print(f'Creating new population')
            pop = Population(neat_config)

    pop.add_reporter(StdOutReporter(True))
    pop.add_reporter(StatisticsReporter())
    pop.add_reporter(Checkpointer(generation_interval=1, filename_prefix=f'{folder}/checkpoint-'))

    return pop


def evaluate_fitness(preset: int, generation: int, genomes: List[Tuple[int, DefaultGenome]], config: Config) -> None:
    pool = Pool(max(os.cpu_count() - 1, 1))
    manager = Manager()
    lock = manager.Lock()
    queue = manager.Queue()
    counter = manager.Value('i', 0)

    gr_folder = f'./game-results-{preset}'

    if not os.path.isdir(gr_folder):
        os.mkdir(gr_folder)

    if os.path.exists(f'{gr_folder}/game-result-{generation}.json'):
        os.remove(f'{gr_folder}/game-result-{generation}.json')

    pool.starmap(process_game, [
        [preset, genome, config, lock, queue, counter] for genome_id, genome in genomes
    ])

    gs_list = []
    gs_json = []

    while not queue.empty():
        game_result = queue.get()  # type: GameResult
        gs_list.append(game_result)
        gs_json.append(vars(game_result))
        genome = list(filter(lambda item: item[0] == game_result.genome_key, genomes))[0][1]
        genome.fitness = game_result.fitness

    gs_json.sort(key=lambda game_json: (game_json['fitness']), reverse=True)

    if generation > 0:
        number = generation - 1
        with open(f'{gr_folder}/game-result-{number}.json', 'w') as file:
            json.dump(gs_json, file, indent=2)

    print()


def process_game(preset: int, genome: DefaultGenome, config: Config, lock: Lock, queue: Queue, counter: Value) -> None:
    game = game_setup(preset)
    play_game(genome, config, game, False)
    game_result = GameResult(genome, game)

    lock.acquire()
    counter.value += 1
    print(f'{counter.value:>3}. {game_result}')
    lock.release()

    queue.put(game_result)


def play_game(genome: DefaultGenome, config: Config, game: Game, render: bool, game_map: GameMap = None) -> None:
    if game_map is None:
        game.reset_game(create_game_map=True)
    else:
        game.game_map = game_map
        game.reset_game(create_game_map=False)

    network = FeedForwardNetwork.create(genome, config)

    if render:
        game.game_map.genome_id = genome.key
        game.game_map.save()

    game.increase_round()

    while True:
        game.player_id = Game.BluePlayer
        player_move = play_move(network, game)

        if render:
            game.game_map.save(player_move=player_move)

        if game.has_ended():
            break

        game.player_id = Game.RedPlayer

        if game.is_red_simulated():
            player_move = play_simulated(game)

            if render:
                game.game_map.save(player_move=player_move)

            if game.has_ended():
                break

        game.increase_round()


def play_simulated(game: Game) -> Dict:
    player_move = game.state_parser.simulate_move()
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

    game.save_state()
    return player_move


def get_fitness(comb):
    payoff = [
        (-1, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 1, 0, 0),
        (1, 0, 0, 0),
        (-1, -1, 0, -1),
        (-1, -2, 0, -2),
        (-1, -3, 0, -3),
        (-1, -4, 0, -4),
        (-1, -5, 0, -5),
        (-1, -6, 0, -6),
        (-1, -7, 0, -7),
        (-1, -8, 0, -8),
        (-1, -9, 0, -9),
        (-1, -10, 0, -10),
        (-1, -11, 0, -11),
        (-1, -12, 0, -12),
        (-1, -13, 0, -13),
        (-1, -14, 0, -14),
        (-1, -15, 0, -15),
        (-1, -16, 0, -16),
        (-1, -17, 0, -17),
        (-1, -18, 0, -18),
        (-1, -19, 0, -19),
        (0, -1, 0, -1),
        (0, -2, 0, -2),
        (0, -3, 0, -3),
        (0, -4, 0, -4),
        (0, -5, 0, -5),
        (0, -6, 0, -6),
        (0, -7, 0, -7),
        (0, -8, 0, -8),
        (0, -9, 0, -9),
        (0, -10, 0, -10),
        (0, -11, 0, -11),
        (0, -12, 0, -12),
        (0, -13, 0, -13),
        (0, -14, 0, -14),
        (0, -15, 0, -15),
        (0, -16, 0, -16),
        (0, -17, 0, -17),
        (0, -18, 0, -18),
        (0, -19, 0, -19),
        (0, -1, -1, -1),
        (0, -2, -1, -2),
        (0, -3, -1, -3),
        (0, -4, -1, -4),
        (0, -5, -1, -5),
        (0, -6, -1, -6),
        (0, -7, -1, -7),
        (0, -8, -1, -8),
        (0, -9, -1, -9),
        (0, -10, -1, -10),
        (0, -11, -1, -11),
        (0, -12, -1, -12),
        (0, -13, -1, -13),
        (0, -14, -1, -14),
        (0, -15, -1, -15),
        (0, -16, -1, -16),
        (0, -17, -1, -17),
        (0, -18, -1, -18),
        (0, -19, -1, -19),
        (-1, -1, -1, -1),
        (-1, -2, -1, -2),
        (-1, -3, -1, -3),
        (-1, -4, -1, -4),
        (-1, -5, -1, -5),
        (-1, -6, -1, -6),
        (-1, -7, -1, -7),
        (-1, -8, -1, -8),
        (-1, -9, -1, -9),
        (-1, -10, -1, -10),
        (-1, -11, -1, -11),
        (-1, -12, -1, -12),
        (-1, -13, -1, -13),
        (-1, -14, -1, -14),
        (-1, -15, -1, -15),
        (-1, -16, -1, -16),
        (-1, -17, -1, -17),
        (-1, -18, -1, -18),
        (-1, -19, -1, -19),
        (-1, -20, -1, -20),
        (1, -1, -1, -1),
        (1, -2, -1, -2),
        (1, -3, -1, -3),
        (1, -4, -1, -4),
        (1, -5, -1, -5),
        (1, -6, -1, -6),
        (1, -7, -1, -7),
        (1, -8, -1, -8),
        (1, -9, -1, -9),
        (1, -10, -1, -10),
        (1, -11, -1, -11),
        (1, -12, -1, -12),
        (1, -13, -1, -13),
        (1, -14, -1, -14),
        (1, -15, -1, -15),
        (1, -16, -1, -16),
        (1, -17, -1, -17),
        (1, -18, -1, -18),
        (1, -19, -1, -19),
    ]

    payoff_dict = {}

    for idx, key in enumerate(payoff):
        payoff_dict[key] = idx + 1

    return payoff_dict[comb] / len(payoff_dict)


def play_move(network: FeedForwardNetwork, game: Game) -> Dict:
    player_id = game.player_id
    player = game.get_player(player_id)
    enemy_id = Game.BluePlayer if player_id == Game.RedPlayer else Game.RedPlayer

    output = network.activate(game.state_parser.encode_state())
    player_move = game.state_parser.decode_state(output)

    move_type = player_move['move_type']
    source_tile = player_move['source_tile']
    target_tile = player_move['target_tile']
    troops = player_move['troops']
    guided = player_move['guided']

    prev_my_tiles = game.get_tile_count(player_id)
    prev_my_troops = game.get_troop_count(player_id)
    prev_enemy_tiles = game.get_tile_count(enemy_id)
    prev_enemy_troops = game.get_troop_count(enemy_id)

    if move_type == Game.ProductionMove:
        game.production_move(source_tile)
    elif move_type == Game.AttackMove:
        game.attack_move(source_tile, target_tile, troops)
    elif move_type == Game.TransportMove:
        game.transport_move(source_tile, target_tile, troops)

    after_my_tiles = game.get_tile_count(player_id)
    after_my_troops = game.get_troop_count(player_id)
    after_enemy_tiles = game.get_tile_count(enemy_id)
    after_enemy_troops = game.get_troop_count(enemy_id)

    comp_my_tiles = after_my_tiles - prev_my_tiles
    comp_my_troops = after_my_troops - prev_my_troops
    comp_enemy_tiles = after_enemy_tiles - prev_enemy_tiles
    comp_enemy_troops = after_enemy_troops - prev_enemy_troops

    move_fitness = get_fitness((comp_my_tiles, comp_my_troops, comp_enemy_tiles, comp_enemy_troops))

    player.per_move_fitness.append(move_fitness)

    if guided:
        player.guided_moves += 1

    game.save_state()
    return player_move
