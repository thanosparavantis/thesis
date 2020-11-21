import math

import matplotlib.pyplot as plt
import neat
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle

import Game
import StateParser


class GenomeGraph:
    def __init__(self, game: Game, nn_parser: StateParser):
        self._figure = None
        self._axes = None
        self._game = game
        self._nn_parser = nn_parser
        self._blue_genome = None
        self._red_genome = None

    def set_genomes(self, blue_genome: neat.DefaultGenome, red_genome: neat.DefaultGenome):
        self._blue_genome = blue_genome
        self._red_genome = red_genome

    def _render_genome(self, axis: Axes, genome: neat.DefaultGenome):
        player_id = self._game.get_player_id()
        player = self._game.get_player(player_id)
        hidden_node_keys = list(genome.nodes.keys())

        for i in range(3):
            hidden_node_keys.remove(i)

        node_coords = dict()

        state = self._nn_parser.encode_state()
        input_key = -1
        tile = 0
        for i in range(self._game.MapWidth):
            for j in range(self._game.MapHeight):
                coords = self._game.get_tile_coords(tile)
                node = Circle(coords, 0.1, color=player.get_tile_color())
                axis.add_patch(node)

                axis.text(
                    x=coords[0],
                    y=coords[1] + 0.5,
                    s=state[tile],
                    color='black',
                    fontfamily='monospace',
                    fontsize='medium',
                    horizontalalignment='center',
                    verticalalignment='center'
                )

                node_coords[input_key] = coords
                input_key -= 1
                tile += 1

        hidden_columns = math.ceil(len(hidden_node_keys) / 3)
        counter = 0

        for i in range(7, 8 + hidden_columns):
            height = 2.5

            for j in range(0, 3):
                if counter == len(hidden_node_keys):
                    break

                coords = (i, height)
                node = Circle(coords, 0.1)
                axis.add_patch(node)
                node_coords[hidden_node_keys[counter]] = coords
                counter += 1
                height += 1

        output_key = 0
        height = 2.5
        for i in range(0, 3):
            coords = (7 + hidden_columns, height)
            node = Circle(coords, 0.1, color='green')
            axis.add_patch(node)
            node_coords[output_key] = coords
            output_key += 1
            height += 1

        connections = list(genome.connections.values())

        for connection in connections:
            node_one_key = connection.key[0]
            node_one_coords = node_coords[node_one_key]
            node_two_key = connection.key[1]
            node_two_coords = node_coords[node_two_key]

            axis.plot(
                [node_one_coords[0], node_two_coords[0]],
                [node_one_coords[1], node_two_coords[1]],
                alpha=0.8 if connection.enabled else 0.2,
                color='gray')

        axis.set_xticks(range(10 + hidden_columns))
        axis.set_yticks(range(7))

    def render(self):
        if self._figure is None:
            self._figure, self._axes = plt.subplots(1, 2)

        blue_nn_axis = self._axes[0]
        blue_nn_axis.cla()
        red_nn_axis = self._axes[1]
        red_nn_axis.cla()

        plt.ion()
        plt.show()

        self._render_genome(blue_nn_axis, self._blue_genome)
        self._render_genome(red_nn_axis, self._red_genome)

        plt.pause(0.001)
