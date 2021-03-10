import os
import shutil
import threading
from typing import Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import RegularPolygon

from game import Game
from state_parser import StateParser


class GameMap:
    SavePath = '/media/thanos/Thanos Paravantis/thesis'
    DefaultSavePath = './games'

    def __init__(self, game: Game, state_parser: StateParser):
        self.game = game
        self.state_parser = state_parser
        self.figure, self.axis = plt.subplots()  # type: Figure, Axes
        self.blue_id = 0
        self.red_id = 0
        self.player_move = None
        self.generation = 0

        self.save_path = GameMap.SavePath if os.path.isdir(GameMap.SavePath) else GameMap.DefaultSavePath

    def render_tile(self, tile: Tuple[int, int], poly_xy: Tuple[float, float], encoded_value: float):
        tile_owner_id = self.game.get_tile_owner(tile)
        tile_owner = self.game.get_player(tile_owner_id)
        troops = self.game.get_tile_troops(tile)
        tile_alpha = max(0.5, troops / Game.TileTroopMax)

        self.axis.add_patch(
            RegularPolygon(
                xy=poly_xy,
                numVertices=6,
                radius=0.8,
                alpha=tile_alpha,
                facecolor=tile_owner.tile_color)
        )

        if troops > 0:
            self.axis.text(
                x=poly_xy[0],
                y=poly_xy[1] + 0.2,
                s=f'{troops}',
                fontfamily='monospace',
                fontsize='medium',
                horizontalalignment='center',
                verticalalignment='center'
            )

        self.axis.text(
            x=poly_xy[0],
            y=poly_xy[1] - 0.1,
            s=str(tile),
            alpha=0.3,
            fontfamily='monospace',
            fontsize='x-small',
            horizontalalignment='center',
            verticalalignment='center'
        )

        self.axis.text(
            x=poly_xy[0],
            y=poly_xy[1] - 0.4,
            s=str(encoded_value),
            alpha=0.3,
            fontfamily='monospace',
            fontsize='x-small',
            horizontalalignment='center',
            verticalalignment='center'
        )

    def create_title(self):
        if self.player_move is None:
            return 'Game Overview'

        if self.game.has_ended():
            winner = self.game.get_winner()

            if winner == Game.BluePlayer:
                return 'Blue won the game!'
            elif winner == Game.RedPlayer:
                return 'Red won the game!'
            else:
                return 'Nobody won the game!'

        move_type = self.player_move['move_type']
        source_tile = self.player_move['source_tile']
        target_tile = self.player_move['target_tile']
        troops = self.player_move['troops']
        guided = self.player_move['guided']

        move_text = '*' if guided else ''

        if move_type == Game.ProductionMove:
            move_text += f'Production Move {source_tile}'
        elif move_type == Game.AttackMove:
            move_text += f'Attack Move {source_tile} → {target_tile} with {troops} troops'
        elif move_type == Game.TransportMove:
            move_text += f'Transport Move {source_tile} → {target_tile} with {troops} troops'
        else:
            move_text += 'Idle Move'

        return move_text

    def create_subtitle(self):
        blue_player = 'Blue' if self.blue_id == 0 else f'Blue {self.blue_id}'
        red_player = 'Red' if self.blue_id == 0 else f'Red {self.red_id}'
        rounds = self.game.get_round()
        player_id = self.game.get_player_id() if rounds > 0 else 0
        blue_fitness, red_fitness = self.game.get_fitness()

        return f'Gen:{self.generation:^5}' \
               f'{blue_player:^8} vs {red_player:^8}' \
               f'{"":5}' \
               f'{rounds}.{player_id}' \
               f'{"":>5}' \
               f'Fitness:{blue_fitness:>6.0f} / {red_fitness:<6.0f}'

    def render(self, title: str = None, subtitle: str = None, show=True) -> None:
        if show:
            plt.ion()
            plt.show()
            plt.pause(0.001)

        title = title or self.create_title()
        subtitle = subtitle or self.create_subtitle()

        self.axis.cla()

        self.figure.suptitle(title)
        self.axis.set_title(subtitle)
        plt.setp(self.axis.get_xticklabels(), visible=False)
        plt.setp(self.axis.get_yticklabels(), visible=False)
        self.axis.tick_params(axis='both', which='both', length=0)
        self.axis.set_aspect('equal')
        self.axis.set_xticks(range(1, 11))
        self.axis.set_yticks(range(1, 9))

        state = self.state_parser.encode_state()

        self.render_tile(tile=(0, 0), poly_xy=(1.0, 7.0), encoded_value=state[0])
        self.render_tile(tile=(0, 1), poly_xy=(2.4, 7.0), encoded_value=state[1])
        self.render_tile(tile=(0, 2), poly_xy=(3.8, 7.0), encoded_value=state[2])
        self.render_tile(tile=(0, 3), poly_xy=(5.2, 7.0), encoded_value=state[3])
        self.render_tile(tile=(0, 4), poly_xy=(6.6, 7.0), encoded_value=state[4])
        self.render_tile(tile=(0, 5), poly_xy=(8.0, 7.0), encoded_value=state[5])

        self.render_tile(tile=(1, 0), poly_xy=(1.7, 5.8), encoded_value=state[6])
        self.render_tile(tile=(1, 1), poly_xy=(3.1, 5.8), encoded_value=state[7])
        self.render_tile(tile=(1, 2), poly_xy=(4.5, 5.8), encoded_value=state[8])
        self.render_tile(tile=(1, 3), poly_xy=(5.9, 5.8), encoded_value=state[9])
        self.render_tile(tile=(1, 4), poly_xy=(7.3, 5.8), encoded_value=state[10])
        self.render_tile(tile=(1, 5), poly_xy=(8.7, 5.8), encoded_value=state[11])

        self.render_tile(tile=(2, 0), poly_xy=(1.0, 4.6), encoded_value=state[12])
        self.render_tile(tile=(2, 1), poly_xy=(2.4, 4.6), encoded_value=state[13])
        self.render_tile(tile=(2, 2), poly_xy=(3.8, 4.6), encoded_value=state[14])
        self.render_tile(tile=(2, 3), poly_xy=(5.2, 4.6), encoded_value=state[15])
        self.render_tile(tile=(2, 4), poly_xy=(6.6, 4.6), encoded_value=state[16])
        self.render_tile(tile=(2, 5), poly_xy=(8.0, 4.6), encoded_value=state[17])

        self.render_tile(tile=(3, 0), poly_xy=(1.7, 3.4), encoded_value=state[18])
        self.render_tile(tile=(3, 1), poly_xy=(3.1, 3.4), encoded_value=state[19])
        self.render_tile(tile=(3, 2), poly_xy=(4.5, 3.4), encoded_value=state[20])
        self.render_tile(tile=(3, 3), poly_xy=(5.9, 3.4), encoded_value=state[21])
        self.render_tile(tile=(3, 4), poly_xy=(7.3, 3.4), encoded_value=state[22])
        self.render_tile(tile=(3, 5), poly_xy=(8.7, 3.4), encoded_value=state[23])

        self.render_tile(tile=(4, 0), poly_xy=(1.0, 2.2), encoded_value=state[24])
        self.render_tile(tile=(4, 1), poly_xy=(2.4, 2.2), encoded_value=state[25])
        self.render_tile(tile=(4, 2), poly_xy=(3.8, 2.2), encoded_value=state[26])
        self.render_tile(tile=(4, 3), poly_xy=(5.2, 2.2), encoded_value=state[27])
        self.render_tile(tile=(4, 4), poly_xy=(6.6, 2.2), encoded_value=state[28])
        self.render_tile(tile=(4, 5), poly_xy=(8.0, 2.2), encoded_value=state[29])

        self.render_tile(tile=(5, 0), poly_xy=(1.7, 1.0), encoded_value=state[30])
        self.render_tile(tile=(5, 1), poly_xy=(3.1, 1.0), encoded_value=state[31])
        self.render_tile(tile=(5, 2), poly_xy=(4.5, 1.0), encoded_value=state[32])
        self.render_tile(tile=(5, 3), poly_xy=(5.9, 1.0), encoded_value=state[33])
        self.render_tile(tile=(5, 4), poly_xy=(7.3, 1.0), encoded_value=state[34])
        self.render_tile(tile=(5, 5), poly_xy=(8.7, 1.0), encoded_value=state[35])

    def save(self, render=True):
        if not os.path.isdir(self.save_path):
            os.mkdir(self.save_path)

        generation_folder = f'{self.save_path}/generation-{self.generation}'

        if not os.path.isdir(generation_folder):
            os.mkdir(generation_folder)

        game_folder = f'{generation_folder}/blue-{self.blue_id}-red-{self.red_id}'

        if not os.path.isdir(game_folder):
            os.mkdir(game_folder)

        rounds = self.game.get_round()
        player_id = self.game.get_player_id()

        if rounds == 0:
            game_file = f'round-{rounds}-start'
        else:
            game_file = f'round-{rounds}-player-{player_id}'

        if render:
            self.render(show=False)

        self.figure.savefig(f'{game_folder}/{game_file}.png')
