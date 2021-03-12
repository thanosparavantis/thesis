import glob
import os
from threading import Thread, Lock
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


def pop_setup(neat_config) -> Population:
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
    threads = []
    lock = Lock()

    if os.path.exists(f'./logs/generation-{generation}.log'):
        os.remove(f'./logs/generation-{generation}.log')

    for genome_id, genome in genomes:
        thread = Thread(name=f'Genome-{genome_id}', target=process_game, daemon=True, args=[genome, config, generation, lock])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print()


def process_game(genome: DefaultGenome, config: Config, generation: int, lock: Lock) -> None:
    game = Game()
    play_game(genome, config, game, False)

    fitness = game.get_fitness()

    rounds = game.get_round()
    blue_tiles = game.get_tile_count(Game.BluePlayer)
    red_tiles = game.get_tile_count(Game.RedPlayer)
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
               f'Fitness: {fitness:>6.1f}' \
               f'{"":2}' \
               f'Winner: {winner:^4}'

    lock.acquire()

    print(log_text)

    with open(f'./logs/generation-{generation}.log', 'a') as file:
        print(log_text, file=file)

    lock.release()

    genome.fitness = fitness


def play_game(genome: DefaultGenome, config: Config, game: Game, render: bool, game_map: GameMap = None) -> None:
    game.reset_game()
    game.game_map = game_map

    network = FeedForwardNetwork.create(genome, config)

    if render:
        game.game_map.genome_id = genome.key
        game.game_map.render()

    game.increase_round()

    while True:
        game.set_player_id(Game.BluePlayer)
        player_move = play_simulated(game)

        if render:
            game.game_map.render(player_move=player_move)

        if game.has_ended():
            break

        game.set_player_id(Game.RedPlayer)
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
