import json
import json
import os
import re
import secrets
from multiprocessing import Pool, Lock, Manager, Value
from multiprocessing.queues import Queue
from typing import Dict, List

from neat import Checkpointer, Population, StdOutReporter, StatisticsReporter, DefaultGenome, Config
from neat.nn import FeedForwardNetwork
from neat.six_util import iteritems

from game import Game
from game_map import GameMap
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


def get_folder_contents(path) -> List[str]:
    files = os.listdir(path)
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    files = sorted(files, key=alphanum_key)
    return files


def pop_blue_setup(neat_config: Config) -> Population:
    return pop_setup(neat_config, 'blue')


def pop_red_setup(neat_config: Config) -> Population:
    return pop_setup(neat_config, 'red')


def pop_setup(neat_config: Config, folder: str) -> Population:
    if not os.path.isdir('./checkpoints'):
        os.mkdir('./checkpoints')

    if not os.path.isdir(f'./checkpoints/{folder}'):
        os.mkdir(f'./checkpoints/{folder}')

    ckp_list = get_folder_contents(f'./checkpoints/{folder}')

    if len(ckp_list) > 0:
        ckp_file = f'./checkpoints/{folder}/{ckp_list[-1]}'
        print(f'Loading checkpoint: {ckp_file}')
        pop = Checkpointer.restore_checkpoint(ckp_file)
    else:
        print(f'Creating new population')
        pop = Population(neat_config)

    pop.add_reporter(StdOutReporter(True))
    pop.add_reporter(StatisticsReporter())
    pop.add_reporter(Checkpointer(1, 300, f'./checkpoints/{folder}/checkpoint-'))

    return pop


def evaluate_fitness(blue_pop: Population, red_pop: Population, config: Config) -> None:
    if blue_pop.generation != red_pop.generation:
        raise Exception("The generation of blue genomes is not in sync with the generation of red genomes.")

    blue_genomes = list(iteritems(blue_pop.population))
    red_genomes = list(iteritems(red_pop.population))
    generation = blue_pop.generation

    pool = Pool()
    manager = Manager()
    lock = manager.Lock()
    queue = manager.Queue()
    counter = manager.Value('i', 0)

    if not os.path.isdir('./game-results'):
        os.mkdir('./game-results')

    if os.path.exists(f'./game-results/game-result-{generation}.json'):
        os.remove(f'./game-results/game-result-{generation}.json')

    genome_pairs = []
    blue_list = list(blue_pop.population.values())
    red_list = list(red_pop.population.values())
    blue_size = len(blue_pop.population)
    red_size = len(red_pop.population)

    if blue_size == red_size:
        for index, (blue_key, blue_genome) in enumerate(blue_genomes):
            genome_pairs.append((blue_genome, red_genomes[index][1]))
    elif blue_size > red_size:
        for index, (blue_key, blue_genome) in enumerate(blue_genomes):
            if index <= red_size - 1:
                genome_pairs.append((blue_genome, red_genomes[index][1]))
            else:
                genome_pairs.append((blue_genome, secrets.choice(red_list)))
    elif blue_size < red_size:
        for index, (red_key, red_genome) in enumerate(red_genomes):
            if index <= blue_size - 1:
                genome_pairs.append((blue_genomes[index][1], red_genome))
            else:
                genome_pairs.append((secrets.choice(blue_list), red_genome))

    pool.starmap(
        process_game,
        [[blue_genome, red_genome, config, lock, queue, counter] for blue_genome, red_genome in genome_pairs]
    )

    game_results = []

    while not queue.empty():
        game_result = queue.get()  # type: GameResult
        game_results.append(vars(game_result))
        blue_genome = list(filter(lambda item: item[0] == game_result.blue_key, blue_genomes))[0][1]
        red_genome = list(filter(lambda item: item[0] == game_result.red_key, red_genomes))[0][1]
        blue_genome.fitness = game_result.blue_fitness
        red_genome.fitness = game_result.red_fitness

    blue_pop.run(lambda genomes, cfg: None, 1)
    red_pop.run(lambda genomes, cfg: None, 1)

    game_results.sort(key=lambda game_json: game_json['rounds'], reverse=True)

    if generation > 0:
        number = generation - 1
        with open(f'./game-results/game-result-{number}.json', 'w') as file:
            json.dump(game_results, file, indent=2)

    print()


def process_game(blue_genome: DefaultGenome, red_genome: DefaultGenome, config: Config, lock: Lock, queue: Queue,
                 counter: Value) -> None:
    game = Game()
    play_game(blue_genome, red_genome, config, game, False)
    game_result = GameResult(blue_genome, red_genome, game)

    lock.acquire()
    counter.value += 1
    print(f'{counter.value:>3}. {game_result}')
    lock.release()

    queue.put(game_result)


def play_game(blue_genome: DefaultGenome, red_genome: DefaultGenome, config: Config, game: Game, render: bool,
              game_map: GameMap = None) -> None:
    if game_map is None:
        game.reset_game(create_game_map=True)
    else:
        game.game_map = game_map
        game.reset_game(create_game_map=False)

    blue_net = FeedForwardNetwork.create(blue_genome, config)
    red_net = FeedForwardNetwork.create(red_genome, config)

    if render:
        game.game_map.blue_key = blue_genome.key
        game.game_map.red_key = red_genome.key
        game.game_map.save()

    game.increase_round()

    while True:
        game.player_id = Game.BluePlayer
        player_move = play_move(blue_net, game)

        if render:
            game.game_map.save(player_move=player_move)

        if game.has_ended():
            break

        game.player_id = Game.RedPlayer
        player_move = play_move(red_net, game)

        if render:
            game.game_map.save(player_move=player_move)

        if game.has_ended():
            break

        game.increase_round()


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
    comp_my_troops = (after_my_troops - prev_my_troops) / Game.TileTroopMax
    comp_enemy_tiles = prev_enemy_tiles - after_enemy_tiles
    comp_enemy_troops = (prev_enemy_troops - after_enemy_troops) / Game.TileTroopMax

    move_fitness = sum([comp_my_tiles, comp_my_troops, comp_enemy_tiles, comp_enemy_troops]) / 4

    player.per_move_fitness.append(move_fitness)

    game.save_state()
    return player_move
