import glob
import json
import os
from multiprocessing import Pool, Lock, Manager
from multiprocessing.queues import Queue
from typing import Dict, Tuple, List

from neat import Checkpointer, Population, StdOutReporter, StatisticsReporter, DefaultGenome, Config
from neat.nn import FeedForwardNetwork

from game import Game
from game_map import GameMap
from game_presets import GamePresetOne, GamePresetTwo
from game_result import GameResult


def print_signature(title):
    print('=' * 50)
    print(f'  {title}')
    print('=' * 50)
    print('* Athanasios Paravantis')
    print('* P16112')
    print('* thanosparavantis@gmail.com')
    print('=' * 50)
    print()


def game_setup(preset: int) -> Game:
    if preset == 1:
        return GamePresetOne()
    elif preset == 2:
        return GamePresetTwo()
    else:
        return Game()


def pop_setup(neat_config: Config, preset: int, ckp_number: int = None) -> Population:
    folder = f'./checkpoints-{preset}'
    filename = f'checkpoint-{ckp_number}'

    if ckp_number:
        ckp_file = f'{folder}/{filename}'
        print(f'Loading predefined checkpoint: {ckp_file}')
        pop = Checkpointer.restore_checkpoint(ckp_file)
    else:

        if not os.path.isdir(folder):
            os.mkdir(folder)

        ckp_list = glob.glob(f'{folder}/*')

        if len(ckp_list) > 0:
            ckp_file = max(ckp_list, key=os.path.getctime)
            print(f'Loading checkpoint: {ckp_file}')
            pop = Checkpointer.restore_checkpoint(ckp_file)
        else:
            print(f'Creating new population')
            pop = Population(neat_config)

    pop.add_reporter(StdOutReporter(True))
    pop.add_reporter(StatisticsReporter())
    pop.add_reporter(Checkpointer(generation_interval=1, filename_prefix=f'{folder}/checkpoint-'))

    return pop


def evaluate_fitness(preset: int, generation: int, genomes: List[Tuple[int, DefaultGenome]], config: Config) -> None:
    pool = Pool(processes=12)
    manager = Manager()
    lock = manager.Lock()
    queue = manager.Queue()

    gr_folder = f'./game-results-{preset}'

    if not os.path.isdir(gr_folder):
        os.mkdir(gr_folder)

    if os.path.exists(f'{gr_folder}/game-result-{generation}.json'):
        os.remove(f'{gr_folder}/game-result-{generation}.json')

    pool.starmap(process_game, [
        [preset, genome, config, lock, queue] for genome_id, genome in genomes
    ])

    game_results = []

    while not queue.empty():
        game_result = queue.get()  # type: GameResult
        game_results.append(vars(game_result))
        genome = list(filter(lambda item: item[0] == game_result.genome_key, genomes))[0][1]
        genome.fitness = game_result.fitness

    game_results.sort(key=lambda game_json: (game_json['fitness']), reverse=True)

    if generation > 0:
        number = generation - 1
        with open(f'{gr_folder}/game-result-{number}.json', 'a') as file:
            json.dump(game_results, file, indent=2)

    print()


def process_game(preset: int, genome: DefaultGenome, config: Config, lock: Lock, queue: Queue) -> None:
    game = game_setup(preset)
    play_game(genome, config, game, False)
    game_result = GameResult(genome, game)

    lock.acquire()
    print(game_result)
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
        # player_move = play_simulated(game)

        # if render:
        #     game.game_map.render(player_move=player_move)
        #
        # if game.has_ended():
        #     break

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


def play_move(network: FeedForwardNetwork, game: Game) -> Dict:
    output = network.activate(game.state_parser.encode_state())
    player_move = game.state_parser.decode_state(output)

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
