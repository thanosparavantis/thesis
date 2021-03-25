import glob
from os import listdir
from os.path import isfile, join

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
from game_map import GameMap
from shared import print_signature, pop_setup, play_game


def main():
    print_signature("Inspection Script")

    neat_config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    ckp_list = [f for f in listdir('./checkpoints/') if isfile(join('./checkpoints/', f))]

    print('Checkpoints:')

    for idx, ckp in enumerate(ckp_list):
        print(f'{idx}. {ckp}')

    print()

    ckp_idx = -1

    while ckp_idx < 0 or ckp_idx >= len(ckp_list):
        ckp_idx = int(input('Enter checkpoint index> '))

    ckp_file = f'./checkpoints/{ckp_list[ckp_idx]}'

    population = pop_setup(neat_config, ckp_file)

    keys = list(population.population.keys())
    key_list = ', '.join(map(str, keys))

    print()
    print(f'Genome Keys:')
    print(key_list)
    print()

    genome_key = input('Enter genome key> ')

    genome = population.population[int(genome_key)]
    game = Game()
    game_map = GameMap()
    game_map.game = game

    play_game(genome, neat_config, game, True, game_map)

    print()
    input('Press Enter to continue...')


if __name__ == '__main__':
    main()
