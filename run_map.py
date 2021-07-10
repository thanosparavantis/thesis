from shared import print_signature, parse_args, game_setup


def main():
    print_signature("Map Overview")

    args = parse_args("Overview of the different game maps.")
    preset = args.preset

    game = game_setup(preset)
    game.game_map.genome_id = 0
    game.game_map.render()

    input()


if __name__ == '__main__':
    main()
