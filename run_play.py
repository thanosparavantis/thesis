import random
import secrets
import time

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
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

    blue_pop = pop_setup('blue', neat_config)
    red_pop = pop_setup('red', neat_config)
    blue_genomes = list(blue_pop.population.values())
    random.shuffle(blue_genomes)
    red_genomes = list(red_pop.population.values())

    while True:
        blue_genome = secrets.choice(blue_genomes)
        red_genome = secrets.choice(red_genomes)
        game = Game()
        play_game(blue_genome, red_genome, neat_config, game, True)
        time.sleep(1)


if __name__ == '__main__':
    main()
