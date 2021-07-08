import json
import os

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game_result import GameResult
from shared import print_signature, pop_setup, play_game, game_setup, parse_args


def main():
    print_signature("Inspection Script")

    args = parse_args("Inspect neural networks through generations and save game plays.")
    preset = args.preset

    file_count = len(os.listdir(f'./game-results-{preset}')) - 1

    if file_count < 0:
        raise Exception("No game results available.")

    ckp_number = int(input(f'Enter game result number (from 0 to {file_count}): '))

    config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')
    population = pop_setup(config, preset, ckp_number)

    file = open(f'./game-results-{preset}/game-result-{ckp_number}.json', 'r')
    game_results = json.load(file)
    file.close()
    game_results = [GameResult(game_json=game_json) for game_json in game_results]

    print()

    for game_result in game_results:
        print(game_result)

    print()

    genome_key = input('Enter genome key: ')

    genome = population.population[int(genome_key)]
    game = game_setup(preset)

    play_game(genome, config, game, True)

    print()
    input('Press Enter to continue...')


if __name__ == '__main__':
    main()
