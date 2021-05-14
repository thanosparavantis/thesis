from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, Config

from shared import pop_setup, print_signature, evaluate_fitness, parse_args


def main():
    print_signature("Evolution Script")

    args = parse_args()

    config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    preset = args.preset
    population = pop_setup(config, preset)

    while True:
        population.run(lambda genomes, config: evaluate_fitness(preset, population.generation, genomes, config), 1)


if __name__ == '__main__':
    main()
