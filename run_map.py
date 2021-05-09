from game_presets import GamePresetOne, GamePresetTwo
from shared import print_signature


def main():
    print_signature("Map Overview")

    game = GamePresetTwo()
    game.game_map.genome_id = 0
    game.game_map.render()

    input()


if __name__ == '__main__':
    main()
