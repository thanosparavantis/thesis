import secrets

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
from game_map import GameMap
from shared import print_signature, pop_setup, play_game


def main():
    print_signature("Play Script")

    neat_config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    population = pop_setup(neat_config)

    game_map = GameMap()

    while True:
        genome = secrets.choice(list(population.population.values()))

        game = Game()
        game_map.game = game

        play_game(genome, neat_config, game, True, game_map)

        print()
        input('Press Enter to continue...')


if __name__ == '__main__':
    main()
