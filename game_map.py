from typing import Tuple

import matplotlib.pyplot as plt
import neat
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import RegularPolygon

from state_parser import StateParser
from game import Game


class GameMap:
    def __init__(self, game: Game, state_parser: StateParser):
        self._game = game
        self._state_parser = state_parser
        self._figure = None
        self._axis = None
        self._blue_genome = None
        self._red_genome = None
        self._player_move = None

    def _render_tile(self, tile: Tuple[int, int], poly_xy: Tuple[float, float], encoded_value: float):
        tile_owner_id = self._game.get_tile_owner(tile)
        tile_owner = self._game.get_player(tile_owner_id)
        troops = self._game.get_tile_troops(tile)
        tile_alpha = max(0.5, troops / Game.TileTroopMax)

        self._axis.add_patch(
            RegularPolygon(
                xy=poly_xy,
                numVertices=6,
                radius=0.8,
                alpha=tile_alpha,
                facecolor=tile_owner.get_tile_color())
        )

        if troops > 0:
            self._axis.text(
                x=poly_xy[0],
                y=poly_xy[1] + 0.2,
                s=f'{troops}',
                fontfamily='monospace',
                fontsize='medium',
                horizontalalignment='center',
                verticalalignment='center'
            )

        self._axis.text(
            x=poly_xy[0],
            y=poly_xy[1] - 0.1,
            s=str(tile),
            alpha=0.3,
            fontfamily='monospace',
            fontsize='x-small',
            horizontalalignment='center',
            verticalalignment='center'
        )

        self._axis.text(
            x=poly_xy[0],
            y=poly_xy[1] - 0.4,
            s=str(encoded_value),
            alpha=0.3,
            fontfamily='monospace',
            fontsize='x-small',
            horizontalalignment='center',
            verticalalignment='center'
        )

    def set_genomes(self, blue_genome: neat.DefaultGenome, red_genome: neat.DefaultGenome):
        self._blue_genome = blue_genome
        self._red_genome = red_genome

    def set_player_move(self, player_move: dict):
        self._player_move = player_move

    def _create_title(self):
        if self._player_move is None:
            return 'Game Overview'

        if self._game.has_ended():
            winner = self._game.get_winner()

            if winner == Game.BluePlayer:
                return 'Blue won the game!'
            elif winner == Game.RedPlayer:
                return 'Red won the game!'
            else:
                return 'Nobody won the game!'

        move_type = self._player_move['move_type']
        tile_A = self._player_move['source_tile']
        tile_B = self._player_move['target_tile']
        troops = self._player_move['troops']

        if move_type == Game.ProductionMove:
            move_text = f'Production Move {tile_A}'
        elif move_type == Game.AttackMove:
            move_text = f'Attack Move {tile_A} → {tile_B} with {troops} troops'
        elif move_type == Game.TransportMove:
            move_text = f'Transport Move {tile_A} → {tile_B} with {troops} troops'
        else:
            move_text = 'Idle Move'

        return move_text

    def _create_subtitle(self):
        g_round = self._game.get_round()
        player_id = self._game.get_player_id()

        if self._blue_genome is not None and self._red_genome is not None:
            blue_id = self._blue_genome.key
            red_id = self._red_genome.key
        else:
            blue_id = '-'
            red_id = '-'

        blue_fitness, red_fitness = self._game.get_fitness()

        return f'{blue_id:^6}/{red_id:^6}{"":>5}{g_round}.{player_id:}{"":>5}{blue_fitness:^6}/{red_fitness:^6}'

    def render(self, title: str = None, subtitle: str = None) -> None:
        title = title or self._create_title()
        subtitle = subtitle or self._create_subtitle()

        if self._figure is None:
            self._figure, self._axis = plt.subplots()  # type: Figure, Axes

        self._axis.cla()
        plt.ion()
        plt.show()
        self._figure.suptitle(title)
        self._axis.set_title(subtitle)
        plt.setp(self._axis.get_xticklabels(), visible=False)
        plt.setp(self._axis.get_yticklabels(), visible=False)
        self._axis.tick_params(axis='both', which='both', length=0)
        self._axis.set_aspect('equal')
        self._axis.set_xticks(range(1, 11))
        self._axis.set_yticks(range(1, 9))

        state = self._state_parser.encode_state()

        self._render_tile(tile=(0, 0), poly_xy=(1.0, 7.0), encoded_value=state[0])
        self._render_tile(tile=(0, 1), poly_xy=(2.4, 7.0), encoded_value=state[1])
        self._render_tile(tile=(0, 2), poly_xy=(3.8, 7.0), encoded_value=state[2])
        self._render_tile(tile=(0, 3), poly_xy=(5.2, 7.0), encoded_value=state[3])
        self._render_tile(tile=(0, 4), poly_xy=(6.6, 7.0), encoded_value=state[4])
        self._render_tile(tile=(0, 5), poly_xy=(8.0, 7.0), encoded_value=state[5])

        self._render_tile(tile=(1, 0), poly_xy=(1.7, 5.8), encoded_value=state[6])
        self._render_tile(tile=(1, 1), poly_xy=(3.1, 5.8), encoded_value=state[7])
        self._render_tile(tile=(1, 2), poly_xy=(4.5, 5.8), encoded_value=state[8])
        self._render_tile(tile=(1, 3), poly_xy=(5.9, 5.8), encoded_value=state[9])
        self._render_tile(tile=(1, 4), poly_xy=(7.3, 5.8), encoded_value=state[10])
        self._render_tile(tile=(1, 5), poly_xy=(8.7, 5.8), encoded_value=state[11])

        self._render_tile(tile=(2, 0), poly_xy=(1.0, 4.6), encoded_value=state[12])
        self._render_tile(tile=(2, 1), poly_xy=(2.4, 4.6), encoded_value=state[13])
        self._render_tile(tile=(2, 2), poly_xy=(3.8, 4.6), encoded_value=state[14])
        self._render_tile(tile=(2, 3), poly_xy=(5.2, 4.6), encoded_value=state[15])
        self._render_tile(tile=(2, 4), poly_xy=(6.6, 4.6), encoded_value=state[16])
        self._render_tile(tile=(2, 5), poly_xy=(8.0, 4.6), encoded_value=state[17])

        self._render_tile(tile=(3, 0), poly_xy=(1.7, 3.4), encoded_value=state[18])
        self._render_tile(tile=(3, 1), poly_xy=(3.1, 3.4), encoded_value=state[19])
        self._render_tile(tile=(3, 2), poly_xy=(4.5, 3.4), encoded_value=state[20])
        self._render_tile(tile=(3, 3), poly_xy=(5.9, 3.4), encoded_value=state[21])
        self._render_tile(tile=(3, 4), poly_xy=(7.3, 3.4), encoded_value=state[22])
        self._render_tile(tile=(3, 5), poly_xy=(8.7, 3.4), encoded_value=state[23])

        self._render_tile(tile=(4, 0), poly_xy=(1.0, 2.2), encoded_value=state[24])
        self._render_tile(tile=(4, 1), poly_xy=(2.4, 2.2), encoded_value=state[25])
        self._render_tile(tile=(4, 2), poly_xy=(3.8, 2.2), encoded_value=state[26])
        self._render_tile(tile=(4, 3), poly_xy=(5.2, 2.2), encoded_value=state[27])
        self._render_tile(tile=(4, 4), poly_xy=(6.6, 2.2), encoded_value=state[28])
        self._render_tile(tile=(4, 5), poly_xy=(8.0, 2.2), encoded_value=state[29])

        self._render_tile(tile=(5, 0), poly_xy=(1.7, 1.0), encoded_value=state[30])
        self._render_tile(tile=(5, 1), poly_xy=(3.1, 1.0), encoded_value=state[31])
        self._render_tile(tile=(5, 2), poly_xy=(4.5, 1.0), encoded_value=state[32])
        self._render_tile(tile=(5, 3), poly_xy=(5.9, 1.0), encoded_value=state[33])
        self._render_tile(tile=(5, 4), poly_xy=(7.3, 1.0), encoded_value=state[34])
        self._render_tile(tile=(5, 5), poly_xy=(8.7, 1.0), encoded_value=state[35])

        plt.pause(0.001)
