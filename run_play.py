from neat import Config, DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation

from game import Game
from game_map import GameMap
from state_parser import StateParser
from shared import print_signature, pop_setup, evaluate_fitness, assign_fitness, play_game


def main():
    print_signature()

    game = Game()
    state_parser = StateParser(game)
    game_map = GameMap(game, state_parser)

    neat_config = Config(
        DefaultGenome,
        DefaultReproduction,
        DefaultSpeciesSet,
        DefaultStagnation,
        './config'
    )

    blue_pop = pop_setup('blue', neat_config)
    red_pop = pop_setup('red', neat_config)

    blue_fitness, red_fitness = evaluate_fitness(
        blue_pop.population,
        red_pop.population,
        neat_config,
        state_parser,
        game,
        game_map,
    )

    blue_genome = blue_pop.run(lambda genomes, config: assign_fitness(genomes, blue_fitness), 1)
    red_genome = red_pop.run(lambda genomes, config: assign_fitness(genomes, red_fitness), 1)

    play_game(blue_genome, red_genome, neat_config, state_parser, game, game_map, True)


if __name__ == '__main__':
    main()
