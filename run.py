import glob
import os

import neat
import numpy as np
from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, StdOutReporter, StatisticsReporter, Checkpointer, Population
from neat.nn import FeedForwardNetwork


def get_fitness(genomes, config):
    idx = 1

    for genome_id, genome in genomes:
        last_fitness = 0
        blue_player = game.get_player(Game.BluePlayer)
        red_player = game.get_player(Game.RedPlayer)

        while True:
            play_round(genome, config)
            game.change_player_id()
            game.reset_moves()
            play_round(genome, config)
            game.reset_moves()

            genome.fitness = np.sum([
                game.get_tile_count(Game.BluePlayer) * blue_player.get_total_production(),
                game.get_tile_count(Game.BluePlayer) * blue_player.get_total_attacks(),
                game.get_tile_count(Game.BluePlayer) * blue_player.get_total_attacks_suceeded(),
                game.get_tile_count(Game.BluePlayer) * blue_player.get_total_attacks_failed(),
                game.get_tile_count(Game.RedPlayer) * red_player.get_total_production(),
                game.get_tile_count(Game.RedPlayer) * red_player.get_total_attacks(),
                game.get_tile_count(Game.RedPlayer) * red_player.get_total_attacks_suceeded(),
                game.get_tile_count(Game.RedPlayer) * red_player.get_total_attacks_failed(),
            ]).item()

            # game.render_map(f'Map Overview', f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome_id}     Fitness: {genome.fitness}')

            if genome.fitness <= last_fitness:
                break

            game.increase_round()
            last_fitness = genome.fitness

        # print(f'{idx}. Genome {genome.key} has fitness: {genome.fitness}')

        # game_stats.add_fitness(genome.fitness)
        # game_stats.add_blue_production(blue_player.get_total_production())
        # game_stats.add_blue_attack_successful(blue_player.get_total_attacks_suceeded())
        # game_stats.add_blue_transport(blue_player.get_total_transports())
        # game_stats.add_red_production(red_player.get_total_production())
        # game_stats.add_red_attack_successful(red_player.get_total_attacks_suceeded())
        # game_stats.add_red_transport(red_player.get_total_transports())
        # game_stats.render_plot()

        game.reset_game()
        idx += 1


def play_round(genome, config):
    # Create a neural network based on the genome
    network = FeedForwardNetwork.create(genome, config)
    player = game.get_player(game.get_player_id())
    # title = f'Round: {game.get_round()}.{game.get_player_id()}     Genome: {genome.key}'
    # subtitle = 'Moves: {}     Fitness: {}'

    while True:
        # First off, if the player ran out of moves then end this round
        if not game.has_moves():
            break

        # Create input for the neural network and store output
        net_output = network.activate(game.create_input())
        output = game.parse_output(net_output)

        # game.render_map(title, subtitle.format(game.get_moves(), genome.fitness))

        # Move cursor A and B on the map
        moved_a = False
        moved_b = False

        # If the output from 0 to 3 has activations, then the neural network wants to move cursor A
        if output[0] and player.can_move_up(Player.CursorA):
            player.move_up(Player.CursorA)
            moved_a = True
        elif output[1] and player.can_move_down(Player.CursorA):
            player.move_down(Player.CursorA)
            moved_a = True
        elif output[2] and player.can_move_left(Player.CursorA):
            player.move_left(Player.CursorA)
            moved_a = True
        elif output[3] and player.can_move_right(Player.CursorA):
            player.move_right(Player.CursorA)
            moved_a = True

        # Update the map if cursor A movement was valid
        # if moved_a:
        #     game.render_map(title, subtitle.format(game.get_moves(), genome.fitness))

        # If the output from 0 to 3 has activations, then the neural network wants to move cursor B
        if output[4] and player.can_move_up(Player.CursorB):
            player.move_up(Player.CursorB)
            moved_b = True
        elif output[5] and player.can_move_down(Player.CursorB):
            player.move_down(Player.CursorB)
            moved_b = True
        elif output[6] and player.can_move_left(Player.CursorB):
            player.move_left(Player.CursorB)
            moved_b = True
        elif output[7] and player.can_move_right(Player.CursorB):
            player.move_right(Player.CursorB)
            moved_b = True

        # Update the map if cursor B movement was valid
        # if moved_b:
        #     game.render_map(title, subtitle.format(game.get_moves(), genome.fitness))

        # If the output 9 has activations, then the neural network wants to make a production move
        if output[9] and game.is_production_move_valid():
            game.production_move()

        # If the output 8 has activations, then the neural network wants to make an attack or transport
        if output[8] and game.is_attack_move_valid():
            game.attack_move()
        elif output[8] and game.is_transport_move_valid():
            game.transport_move()

        # If the neural network made a successful production, attack or transport move, reset moves
        if (output[9] and game.is_production_move_valid()) or (output[8] and game.is_attack_move_valid()):
            game.reset_moves()
        # Otherwise the neural network is probably doing nothing useful, so increment moves
        else:
            game.make_move()


if __name__ == '__main__':
    from game import Game
    from player import Player
    from game_stats import GameStatistics

    game = Game()
    game_stats = GameStatistics()
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
    pop.add_reporter(Checkpointer(1, filename_prefix='./checkpoints/neat-checkpoint-'))
    pop.run(get_fitness, 100)
