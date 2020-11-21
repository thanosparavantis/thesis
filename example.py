from Game import Game
from GameMap import GameMap
from StateParser import StateParser


def main():
    game = Game()
    state_parser = StateParser(game)
    game_map = GameMap(game, state_parser)
    game_map.render()


if __name__ == '__main__':
    main()
