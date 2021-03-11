import glob
import os
from collections import defaultdict
from queue import Queue
from threading import Thread, Lock
from typing import Dict, Tuple, List

from neat import Checkpointer, Population, StdOutReporter, StatisticsReporter, DefaultGenome, Config
from neat.nn import FeedForwardNetwork

from game import Game


def print_signature(title):
    print('=' * 50)
    print(f'  {title}')
    print('=' * 50)
    print('* Athanasios Paravantis')
    print('* P16112')
    print('* thanosparavantis@gmail.com')
    print('=' * 50)
    print()


def pop_setup(name, neat_config) -> Population:
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


def evaluate_fitness(blue_genomes: Dict[int, DefaultGenome], red_genomes: Dict[int, DefaultGenome], config: Config) -> Tuple[Dict[int, float], Dict[int, float]]:
    queue = Queue()
    threads = []
    print_lock = Lock()
    bf_list = defaultdict(float)
    rf_list = defaultdict(float)

    blue_genomes = list(blue_genomes.values())
    red_genomes = list(red_genomes.values())

    if len(blue_genomes) != len(red_genomes):
        raise Exception("The number of blue genomes is not equal to the number of red genomes.")

    games_max = len(blue_genomes)

    for index in range(games_max):
        blue_genome = blue_genomes[index]
        red_genome = red_genomes[index]

        thread = Thread(
            name=f'B{blue_genome.key}R{red_genome.key}',
            target=process_game,
            daemon=True,
            args=[queue, print_lock, blue_genome, red_genome, config]
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    while not queue.empty():
        game_result = queue.get()
        bf_list[game_result['blue_id']] = game_result['blue_fitness']
        rf_list[game_result['red_id']] = game_result['red_fitness']

    return bf_list, rf_list


def process_game(queue: Queue, print_lock: Lock, blue_genome: DefaultGenome, red_genome: DefaultGenome, config: Config) -> None:
    game = Game()

    play_game(blue_genome, red_genome, config, game, False)

    blue_fitness, red_fitness = game.get_fitness()

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

    blue_id = blue_genome.key
    red_id = red_genome.key
    game_name = f'B{blue_id}R{red_id}'

    print_lock.acquire()

    print(
        f'{game_name:<10}'
        f'{"":2}'
        f'Rounds: {rounds:>4}'
        f'{"":2}'
        f'Winner: {winner:^4}'
        f'{"":2}'
        f'Tiles: {blue_tiles:>2} / {red_tiles:<2}'
        f'{"":2}'
        f'Fitness: {blue_fitness:>6.1f} / {red_fitness:<6.1f}'
    )

    print_lock.release()

    queue.put({
        'blue_id': blue_id,
        'blue_fitness': blue_fitness,
        'red_id': red_id,
        'red_fitness': red_fitness
    })


def assign_fitness(genomes: List[Tuple[int, DefaultGenome]], fitness_mapping: Dict[int, float]) -> None:
    for genome_id, genome in genomes:
        genome.fitness = fitness_mapping[genome.key]


def play_game(blue_genome: DefaultGenome, red_genome: DefaultGenome, config: Config, game: Game, render: bool) -> None:
    game.reset_game()

    blue_net = FeedForwardNetwork.create(blue_genome, config)
    red_net = FeedForwardNetwork.create(red_genome, config)

    if render:
        game.game_map.blue_id = blue_genome.key
        game.game_map.red_id = red_genome.key
        game.game_map.render()

    game.increase_round()

    while True:
        game.set_player_id(Game.BluePlayer)
        player_move = play_game_move(blue_net, red_net, game)

        if render:
            game.game_map.render(player_move=player_move)

        if game.has_ended():
            break

        game.set_player_id(Game.RedPlayer)
        player_move = play_game_move(blue_net, red_net, game)

        if render:
            game.game_map.render(player_move=player_move)

        if game.has_ended():
            break

        game.increase_round()


def play_game_move(blue_net: FeedForwardNetwork, red_net: FeedForwardNetwork, game: Game) -> Dict:
    player_id = game.get_player_id()

    net = blue_net if player_id == Game.BluePlayer else red_net
    net_out = net.activate(game.state_parser.encode_state())
    player_move = game.state_parser.decode_state(net_out)

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
