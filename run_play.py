import secrets

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
from game_map import GameMap
from shared import print_signature, pop_blue_setup, pop_red_setup, play_game


def main():
    print_signature("Play Script")

    neat_config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    blue_pop = pop_blue_setup(neat_config)
    red_pop = pop_red_setup(neat_config)

    game_map = GameMap()

    while True:
        blue_genome = secrets.choice(list(blue_pop.population.values()))
        red_genome = secrets.choice(list(red_pop.population.values()))

        game = Game()
        game_map.game = game

        play_game(blue_genome, red_genome, neat_config, game, True, game_map)

        print()
        input('Press Enter to continue...')


if __name__ == '__main__':
    main()
