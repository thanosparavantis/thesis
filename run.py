import glob
import os
from math import sqrt

import neat
import numpy as np
from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, StdOutReporter, StatisticsReporter, Checkpointer, Population
from neat.nn import FeedForwardNetwork

from game_map import GameMap
from nn_parser import NeuralNetworkParser


def get_fitness(genomes, config):
    blue_production = 0
    red_production = 0
    blue_attacks = 0
    red_attacks = 0
    blue_transports = 0
    red_transports = 0

    for genome_id, genome in genomes:
        genome.fitness = 0

        while True:
            has_progress, player_move = make_move(genome, config)
            genome.fitness += evaluate_fitness(player_move)

            if not has_progress or game.get_tiles(game.get_player_id()) == 0:
                break

            game.change_player_id()

            has_progress, player_move = make_move(genome, config)
            genome.fitness += evaluate_fitness(player_move)

            if not has_progress or game.get_tiles(game.get_player_id()) == 0:
                break

            game.change_player_id()
            game.increase_round()

        blue_player = game.get_player(Game.BluePlayer)
        red_player = game.get_player(Game.RedPlayer)

        blue_production += blue_player.get_total_production()
        red_production += red_player.get_total_production()
        blue_attacks += blue_player.get_total_attacks()
        red_attacks += red_player.get_total_attacks()
        blue_transports += blue_player.get_total_transports()
        red_transports += red_player.get_total_transports()

        game.reset_game()

    game_stats.add_blue_production(blue_production)
    game_stats.add_red_production(red_production)
    game_stats.add_blue_attack(blue_attacks)
    game_stats.add_red_attack(red_attacks)
    game_stats.add_blue_transport(blue_transports)
    game_stats.add_red_transport(red_transports)


def evaluate_fitness(player_move):
    fitness = 0
    my_tiles = game.get_tiles(game.get_player_id())
    my_adj_tiles = game.get_tiles_adj(game.get_player_id())
    enemy_tiles = game.get_tiles(Game.RedPlayer if game.get_player_id() == Game.BluePlayer else Game.BluePlayer)
    move_type = player_move["move_type"]
    tile_A = player_move["tile_A"]
    tile_B = player_move["tile_B"]
    troops = player_move["troops"]
    coord_my_tiles = set([coord for tile in my_tiles for coord in tile])
    coord_comb_tiles = set([coord for tile in my_tiles.union(my_adj_tiles) for coord in tile])
    coord_my_adj_tiles = set([coord for tile in my_adj_tiles for coord in tile])
    player_troops = game.get_troop_count(game.get_player_id())
    player_tiles = game.get_tile_count(game.get_player_id())
    can_produce = player_troops % 20 != 0
    can_transport = player_tiles > 1

    s_i, s_j = tile_A
    t_i, t_j = tile_B

    if (move_type == 0 and can_produce) or move_type == 1 or (move_type == 2 and can_transport):
        # +15 fitness all

        fitness += 1

        if 0 <= s_i <= Game.MapWidth - 1:
            fitness += 1

        if 0 <= s_j <= Game.MapHeight - 1:
            fitness += 1

        if s_i in coord_my_tiles:
            fitness += 1

        if s_j in coord_my_tiles:
            fitness += 1

        if t_i in coord_comb_tiles:
            fitness += 1

        if t_j in coord_comb_tiles:
            fitness += 1

        if 0 <= t_i <= Game.MapWidth - 1:
            fitness += 1

        if 0 <= t_j <= Game.MapHeight - 1:
            fitness += 1

        if tile_A in my_tiles:
            fitness += 1

        if tile_A not in enemy_tiles:
            fitness += 1

        if tile_A != tile_B:
            fitness += 1

        if Game.TileTroopMin <= troops <= Game.TileTroopMax:
            fitness += 1

        if tile_A in my_tiles and game.get_map_troops()[s_i, s_j] >= troops:
            fitness += 1

        if Game.TileTroopMin <= troops <= Game.TileTroopMax:
            fitness += 1

    if move_type == 0 and can_produce:
        # + 8 fitness all

        if tile_A in my_tiles and game.get_map_troops()[s_i, s_j] < Game.TileTroopMax:
            fitness += 1

        if game.is_production_move_valid(tile_A):
            fitness += 7

    if move_type == 1:
        # + 8 fitness all

        if t_i in coord_my_adj_tiles:
            fitness += 1

        if t_j in coord_my_adj_tiles:
            fitness += 1

        if tile_B in my_adj_tiles:
            fitness += 1

        if game.is_attack_move_valid(tile_A, tile_B, troops):
            fitness += 5

    if move_type == 2 and can_transport:
        # + 8 fitness all

        if t_i in coord_my_tiles:
            fitness += 1

        if t_j in coord_my_tiles:
            fitness += 1

        if tile_B in my_tiles:
            fitness += 1

        if abs(s_i - t_i) <= 1:
            fitness += 1

        if abs(s_j - t_j) <= 1:
            fitness += 1

        if tile_B not in enemy_tiles:
            fitness += 1

        if tile_B in my_tiles and game.get_map_troops()[t_i, t_j] + troops <= Game.TileTroopMax:
            fitness += 1

        if game.is_transport_move_valid(tile_A, tile_B, troops):
            fitness += 1

    return fitness


def play_game(genome, config, render=False):
    while True:
        has_progress, player_move = make_move(genome, config, render)

        if not has_progress or game.get_tiles(game.get_player_id()) == 0:
            break

        game.change_player_id()

        has_progress, player_move = make_move(genome, config, render)

        if not has_progress or game.get_tiles(game.get_player_id()) == 0:
            break

        game.change_player_id()

        game.increase_round()

    if render:
        game_map.render(
            '',
            f'Game ended...'
        )


def make_move(genome, config, render=False):
    network = FeedForwardNetwork.create(genome, config)
    network_output = network.activate(nn_parser.encode_state())
    player_move = nn_parser.decode_output(network_output)

    move_type = player_move["move_type"]
    tile_A = player_move["tile_A"]
    tile_B = player_move["tile_B"]
    troops = player_move["troops"]

    print(move_type, tile_A, tile_B, troops)

    move = 'Waiting...'
    has_progress = False

    if render:
        print(f'{game.get_round()}.{game.get_player_id()}', f'Type: {move_type}', f'Tile A: {tile_A}', f'Tile B: {tile_B}', f'Troops: {troops}')

        game_map.render(
            f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome.key}     Fitness: {genome.fitness}',
            f'{move}'
        )

    if move_type == 0 and game.is_production_move_valid(tile_A):
        game.production_move(tile_A)
        move = f'Production Move {tile_A}'
        has_progress = True
    elif move_type == 1 and game.is_attack_move_valid(tile_A, tile_B, troops):
        game.attack_move(tile_A, tile_B, troops)
        move = f'Attack Move {tile_A} → {tile_B} with {troops} troops'
        has_progress = True
    elif move_type == 2 and game.is_transport_move_valid(tile_A, tile_B, troops):
        game.is_transport_move_valid(tile_A, tile_B, troops)
        move = f'Transport Move {tile_A} → {tile_B} with {troops} troops'
        has_progress = True

    if render and has_progress:
        game_map.render(
            f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome.key}     Fitness: {genome.fitness}',
            f'{move}'
        )

    return has_progress, player_move


if __name__ == '__main__':
    from game import Game
    from game_stats import GameStatistics

    game = Game()
    game_map = GameMap(game)
    game_stats = GameStatistics()
    nn_parser = NeuralNetworkParser(game)

    neat_config = neat.Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    if not os.path.isdir('./checkpoints'):
        os.mkdir('./checkpoints')

    ckp_list = glob.glob('./checkpoints/*')

    if len(ckp_list) > 0:
        ckp_file = max(ckp_list, key=os.path.getctime)
        print(f'Loading checkpoint: {ckp_file}')
        pop = Checkpointer.restore_checkpoint(ckp_file)
    else:
        print('Creating new population')
        pop = Population(neat_config)

    pop.add_reporter(StdOutReporter(True))
    pop.add_reporter(StatisticsReporter())
    pop.add_reporter(Checkpointer(100, filename_prefix='./checkpoints/neat-checkpoint-'))

    last_genome = None

    while True:
        genome = pop.run(get_fitness, 1)

        game_stats.add_fitness(genome.fitness)
        game_stats.render_plot()

        if genome == last_genome:
            continue
        else:
            last_genome = genome

        play_game(genome, neat_config, render=True)

