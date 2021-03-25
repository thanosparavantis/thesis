import glob
import os
import time
from multiprocessing import Pool, Lock, Manager
from multiprocessing.queues import Queue
from typing import Dict, Tuple, List

from neat import Checkpointer, Population, StdOutReporter, StatisticsReporter, DefaultGenome, Config
from neat.nn import FeedForwardNetwork

from game import Game
from game_map import GameMap


def print_signature(title):
    print('=' * 50)
    print(f'  {title}')
    print('=' * 50)
    print('* Athanasios Paravantis')
    print('* P16112')
    print('* thanosparavantis@gmail.com')
    print('=' * 50)
    print()


def pop_setup(neat_config: Config, ckp_file: str = None) -> Population:
    if ckp_file:
        print(f'Loading predefined checkpoint: {ckp_file}')
        pop = Checkpointer.restore_checkpoint(ckp_file)
    else:
        if not os.path.isdir('./checkpoints'):
            os.mkdir('./checkpoints')

        if not os.path.isdir('./logs'):
            os.mkdir('./logs')

        ckp_list = glob.glob(f'./checkpoints/*')

        if len(ckp_list) > 0:
            ckp_file = max(ckp_list, key=os.path.getctime)
            print(f'Loading checkpoint: {ckp_file}')
            pop = Checkpointer.restore_checkpoint(ckp_file)
        else:
            print(f'Creating new population')
            pop = Population(neat_config)

    pop.add_reporter(StdOutReporter(True))
    pop.add_reporter(StatisticsReporter())
    pop.add_reporter(Checkpointer(generation_interval=1, filename_prefix=f'./checkpoints/generation-'))

    return pop


def evaluate_fitness(generation: int, genomes: List[Tuple[int, DefaultGenome]], config: Config) -> None:
    pool = Pool(processes=10)
    manager = Manager()
    lock = manager.Lock()
    queue = manager.Queue()

    if os.path.exists(f'./logs/generation-{generation}.log'):
        os.remove(f'./logs/generation-{generation}.log')

    pool.starmap(process_game, [[genome, config, generation, lock, queue] for genome_id, genome in genomes])

    while not queue.empty():
        training_data = queue.get()
        genome = list(filter(lambda item: item[0] == training_data[0], genomes))[0][1]
        genome.fitness = training_data[1]

    print()


def process_game(genome: DefaultGenome, config: Config, generation: int, lock: Lock, queue: Queue) -> None:
    game = Game()
    play_game(genome, config, game, False)

    fitness = game.get_fitness()

    rounds = game.rounds
    blue_tiles = game.get_tile_count(Game.BluePlayer)
    blue_troops = game.get_troop_count(Game.BluePlayer)
    red_tiles = game.get_tile_count(Game.RedPlayer)
    red_troops = game.get_troop_count(Game.RedPlayer)
    winner_id = game.get_winner()

    if winner_id == Game.BluePlayer:
        winner = 'Blue'
    elif winner_id == Game.RedPlayer:
        winner = 'Red'
    else:
        winner = '-'

    log_text = f'Genome: {genome.key:>4}' \
               f'{"":2}' \
               f'Rounds: {rounds:>4}' \
               f'{"":2}' \
               f'Tiles: {blue_tiles:>2} / {red_tiles:<2}' \
               f'{"":2}' \
               f'Troops: {blue_troops:>3} / {red_troops:>3}' \
               f'{"":2}' \
               f'Fitness: {fitness:>6.1f}' \
               f'{"":2}' \
               f'Winner: {winner:>4}'

    lock.acquire()

    print(log_text)

    with open(f'./logs/generation-{generation}.log', 'a') as file:
        print(log_text, file=file)

    lock.release()

    queue.put((genome.key, fitness))


def play_game(genome: DefaultGenome, config: Config, game: Game, render: bool, game_map: GameMap = None) -> None:
    if game_map is None:
        game.reset_game(create_game_map=True)
    else:
        game.game_map = game_map
        game.reset_game(create_game_map=False)

    network = FeedForwardNetwork.create(genome, config)

    if render:
        game.game_map.genome_id = genome.key
        game.game_map.render()

    game.increase_round()

    while True:
        # game.player_id = Game.BluePlayer
        # player_move = play_simulated(game)

        # if render:
        #     game.game_map.render(player_move=player_move)

        # if game.has_ended():
        #     break

        # game.player_id = Game.RedPlayer
        player_move = play_move(network, game)

        if render:
            game.game_map.render(player_move=player_move)

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
