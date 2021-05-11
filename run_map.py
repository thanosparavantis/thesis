from game_presets import ExpandAloneFastGame, ConquerEasyEnemyFastGame, ConquerHardEnemyFastGame
from shared import print_signature


def main():
    print_signature("Map Overview")

    game = ConquerHardEnemyFastGame()
    game.game_map.genome_id = 0
    game.game_map.render()

    input()


if __name__ == '__main__':
    main()
