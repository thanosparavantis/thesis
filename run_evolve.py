from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, Config

from shared import pop_setup, print_signature, evaluate_fitness


def main():
    print_signature("Evolution Script")
    config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    preset = int(input('Enter game preset> '))
    population = pop_setup(config, preset)

    population.run(lambda genomes, config: evaluate_fitness(preset, population.generation, genomes, config), 100)


if __name__ == '__main__':
    main()
