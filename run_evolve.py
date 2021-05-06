from neat import DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, Config

from shared import pop_blue_setup, pop_red_setup, print_signature, evaluate_fitness


def main():
    print_signature("Evolution Script")

    config = Config(DefaultGenome, DefaultReproduction, DefaultSpeciesSet, DefaultStagnation, './config')

    blue_pop = pop_blue_setup(config)
    red_pop = pop_red_setup(config)

    while True:
        evaluate_fitness(blue_pop, red_pop, config)


if __name__ == '__main__':
    main()
