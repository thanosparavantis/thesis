import json

from neat import Config, Checkpointer, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
from game_result import GameResult
from shared import print_signature, play_game


def main():
    print_signature("Inspection Script")

    neat_config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    ckp_number = input('Enter checkpoint number> ')
    blue_pop = Checkpointer.restore_checkpoint(f'./checkpoints/blue/checkpoint-{ckp_number}')
    red_pop = Checkpointer.restore_checkpoint(f'./checkpoints/red/checkpoint-{ckp_number}')

    game_results_file = open(f'./game-results/game-result-{ckp_number}.json', 'r')
    game_results = json.load(game_results_file)
    game_results_file.close()
    game_results = [GameResult(game_json=game_json) for game_json in game_results]

    print()

    for game_result in game_results:
        print(game_result)

    print()

    blue_key = input('Enter blue genome key> ')
    red_key = input('Enter red genome key> ')

    blue_genome = blue_pop.population[int(blue_key)]
    red_genome = red_pop.population[int(red_key)]
    game = Game()

    play_game(blue_genome, red_genome, neat_config, game, True)

    print()
    input('Press Enter to continue...')


if __name__ == '__main__':
    main()
