import secrets

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game_map import GameMap
from shared import print_signature, pop_setup, play_game, game_setup


def main():
    print_signature("Play Script")
    neat_config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    preset = int(input('Enter game preset> '))
    game = game_setup(preset)
    population = pop_setup(neat_config, preset)

    game_map = GameMap()

    while True:
        genome = secrets.choice(list(population.population.values()))

        game_map.game = game

        play_game(genome, neat_config, game, True, game_map)

        print()
        input('Press Enter to continue...')


if __name__ == '__main__':
    main()
