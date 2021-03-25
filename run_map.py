import secrets

from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
from game_map import GameMap
from shared import print_signature, pop_setup, play_game


def main():
    print_signature("Map Overview")

    game = Game()
    game.game_map.genome_id = 0
    game.game_map.render()

    input()


if __name__ == '__main__':
    main()
