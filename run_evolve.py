from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, Config

from shared import pop_setup, print_signature, evaluate_fitness, assign_fitness


def main():
    print_signature("Evolution Script")

    neat_config = Config(
        DefaultGenome,
        DefaultReproduction,
        DefaultSpeciesSet,
        DefaultStagnation,
        './config'
    )

    blue_pop = pop_setup('blue', neat_config)
    red_pop = pop_setup('red', neat_config)

    while True:
        blue_fitness, red_fitness = evaluate_fitness(blue_pop.population, red_pop.population, neat_config)
        blue_pop.run(lambda genomes, config: assign_fitness(genomes, blue_fitness), 1)
        red_pop.run(lambda genomes, config: assign_fitness(genomes, red_fitness), 1)


if __name__ == '__main__':
    main()
