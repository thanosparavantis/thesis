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
from NeuralNetworkParser import NeuralNetworkParser


def main():
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
    blue_fitness_max = 0
    red_fitness_max = 0
    blue_fitness = defaultdict(list)
    red_fitness = defaultdict(list)

    for blue_id, blue_genome in blue_genomes.items():
        for red_id, red_genome in red_genomes.items():
            play_game(blue_genome, red_genome, config, nn_parser, game, game_map, False)

            blue_tiles = game.get_tile_count(Game.BluePlayer)
            red_tiles = game.get_tile_count(Game.RedPlayer)
            nature_tiles = game.get_tile_count(Game.NaturePlayer)
            blue_troops = game.get_troop_count(Game.BluePlayer)
            red_troops = game.get_troop_count(Game.RedPlayer)

            blue_fitness_score = 10 * (blue_tiles - red_tiles) + 10 * (blue_tiles - nature_tiles) + (blue_troops - red_troops)
            red_fitness_score = 10 * (red_tiles - blue_tiles) + 10 * (red_tiles - nature_tiles) + (red_troops - blue_troops)

            if blue_tiles == 0:
                status = 'Red Won'
            elif red_tiles == 0:
                status = 'Blue Won'
            else:
                status = 'Tie'

            fitness_record = ''

            if blue_fitness_score > blue_fitness_max:
                blue_fitness_max = blue_fitness_score
                fitness_record = f'Blue highscore ({blue_fitness_score})'
            elif red_fitness_score > red_fitness_max:
                red_fitness_max = red_fitness_score
                fitness_record = f'Red highscore ({red_fitness_score})'
            elif blue_fitness_score > blue_fitness_max and red_fitness_score > red_fitness_max:
                blue_fitness_max = blue_fitness_score
                red_fitness_max = red_fitness_score
                fitness_record = f'New highscore ({blue_fitness_score}/{red_fitness_score})'

            rounds = game.get_round()

            print(f'Genomes: {blue_id:^5}/{red_id:^5} Fitness: {blue_fitness_score:^5}/{red_fitness_score:^5} Rounds: {rounds:^6} Status: {status:<10} {fitness_record}')

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
            # game_stats.render_plot()

            game.reset_game()

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
              render: bool = False) -> None:
    blue_nn = FeedForwardNetwork.create(blue_genome, config)
    red_nn = FeedForwardNetwork.create(red_genome, config)

    if render:
        render_map('Overview', game, game_map, blue_genome, red_genome)

    while True:
        if game.get_tile_count(game.get_player_id()) == 0:
            if render:
                render_map('Red won the game!', game, game_map, blue_genome, red_genome)

            break

        player_move = play_move(blue_genome, red_genome, blue_nn, red_nn, nn_parser, game, game_map, render)

        if player_move['move_type'] == Game.InvalidMove:
            if render:
                render_map('Invalid Move', game, game_map, blue_genome, red_genome)

            break

        game.change_player_id()

        if game.get_tile_count(game.get_player_id()) == 0:
            if render:
                render_map('Blue won the game!', game, game_map, blue_genome, red_genome)

            break

        player_move = play_move(blue_genome, red_genome, blue_nn, red_nn, nn_parser, game, game_map, render)

        if player_move['move_type'] == Game.InvalidMove:
            if render:
                render_map('Invalid Move', game, game_map, blue_genome, red_genome)

            break

        game.change_player_id()

        if game.get_round() == 500:
            if render:
                render_map('Game ended with a Tie', game, game_map, blue_genome, red_genome)

            break

        game.increase_round()


def play_move(blue_genome: neat.DefaultGenome,
              red_genome: neat.DefaultGenome,
              blue_nn: neat.nn.FeedForwardNetwork,
              red_nn: neat.nn.FeedForwardNetwork,
              nn_parser: NeuralNetworkParser,
              game: Game,
              game_map: GameMap,
              render: bool = False) -> Dict:
    network = blue_nn if game.get_player_id() == Game.BluePlayer else red_nn
    network_output = network.activate(nn_parser.encode_state())
    player_move = nn_parser.decode_state_m2(network_output)

    move_type = player_move['move_type']
    tile_A = player_move['tile_A']
    tile_B = player_move['tile_B']
    troops = player_move['troops']

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
        print(f'{game.get_round()}.{game.get_player_id()} {move} {player_move}')

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
    main()
