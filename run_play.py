import time

from game import Game
from game_presets import BlueAgainstRed
from shared import print_signature, parse_args, play_simulated


def main():
    print_signature("Play Script")

    game = BlueAgainstRed()
    game.reset_game(create_game_map=True)
    game.game_map.genome_id = 0

    game.increase_round()
    game.player_id = Game.RedPlayer

    game.game_map.save()

    while True:
        if game.has_ended():
            break

        player_move = play_simulated(game)
        game.game_map.save(player_move=player_move)
        time.sleep(1)
        game.increase_round()


if __name__ == '__main__':
    main()
