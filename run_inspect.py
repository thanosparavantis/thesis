import json

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game_map import GameMap
from game_result import GameResult
from shared import print_signature, pop_setup, play_game, game_setup


def main():
    print_signature("Inspection Script")
    neat_config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    preset = int(input('Enter game preset> '))

    ckp_number = int(input('Enter checkpoint number> '))
    population = pop_setup(neat_config, preset, ckp_number)

    game_results_file = open(f'./game-results-{preset}/game-result-{ckp_number}.json', 'r')
    game_results = json.load(game_results_file)
    game_results_file.close()
    game_results = [GameResult(game_json=game_json) for game_json in game_results]

    print()

    for game_result in game_results:
        print(game_result)

    print()

    genome_key = input('Enter genome key> ')

    genome = population.population[int(genome_key)]
    game = game_setup(preset)

    play_game(genome, neat_config, game, True)

    print()
    input('Press Enter to continue...')


if __name__ == '__main__':
    main()
