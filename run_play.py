import random
import secrets
import time

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
from game_map import GameMap
from shared import print_signature, pop_setup, play_game


def main():
    print_signature("Play Script")

    neat_config = Config(
        DefaultGenome,
        DefaultReproduction,
        DefaultSpeciesSet,
        DefaultStagnation,
        './config'
    )


    game_map = GameMap()

    while True:
        population = pop_setup(neat_config)

        genome = None

        while genome is None:
            genome_id = input('Enter Genome Key> ')

            if len(genome_id) == 0:
                break

            genome_id = int(genome_id)

            if genome_id in population.population:
                genome = population.population[genome_id]

        if genome is None:
            genome = random.choice(list(population.population.values()))

        game = Game()
        game_map.game = game

        play_game(genome, neat_config, game, True, game_map)
        time.sleep(1)


if __name__ == '__main__':
    main()
