from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, Config

from game import Game
from game_map import GameMap
from statistics import Statistics
from shared import pop_setup, print_signature, evaluate_fitness, assign_fitness
from state_parser import StateParser
from visualize import draw_net


def main():
    print_signature()

    game = Game()
    state_parser = StateParser(game)
    game_map = GameMap(game, state_parser)
    game_stats = Statistics(game)

    neat_config = Config(
        DefaultGenome,
        DefaultReproduction,
        DefaultSpeciesSet,
        DefaultStagnation,
        './config'
    )

    blue_pop = pop_setup('blue', neat_config)
    red_pop = pop_setup('red', neat_config)

    for iteration in range(1, 101):
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

        draw_net(config=neat_config, genome=blue_genome, filename='graphs/blue_genome', fmt='png')
        draw_net(config=neat_config, genome=red_genome, filename='graphs/red_genome', fmt='png')

        game_stats.add_blue_fitness(blue_genome.fitness)
        game_stats.add_red_fitness(red_genome.fitness)
        game_stats.render()


if __name__ == '__main__':
    main()
