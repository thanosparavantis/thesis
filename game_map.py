import os
from collections import defaultdict
from typing import Tuple, Dict

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import RegularPolygon

from game_map_tile import GameMapTile


class GameMap:
    SavePath = '/media/thanos/Thanos Paravantis/thesis'
    DefaultSavePath = './games'

    def __init__(self):
        self.game = None
        self.genome_id = None
        self.figure = None  # type: Figure
        self.axis = None  # type: Axes
        self.game_map_tiles = dict()  # type: Dict[Tuple[int, int], GameMapTile]
        self.save_path = GameMap.SavePath if os.path.isdir(GameMap.SavePath) else GameMap.DefaultSavePath

    def create_title(self, player_move: Dict) -> str:
        from game import Game

        if player_move is None:
            return 'Game Overview'

        if self.game.has_ended():
            winner = self.game.get_winner()

            if winner == Game.BluePlayer:
                return 'Blue won the game!'
            elif winner == Game.RedPlayer:
                return 'Red won the game!'
            else:
                return 'Nobody won the game!'

        move_type = player_move['move_type']
        source_tile = player_move['source_tile']
        target_tile = player_move['target_tile']
        troops = player_move['troops']
        guided = player_move['guided']

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

    def create_subtitle(self) -> str:
        rounds = self.game.rounds
        fitness = self.game.get_fitness()

        return f'Genome: {self.genome_id:>4}' \
               f'{"":5}' \
               f'Round: {rounds}' \
               f'{"":>5}' \
               f'Fitness: {fitness:>7.3f}'

    def render_tile(self, tile: Tuple[int, int], poly_xy: Tuple[float, float], encoding_value: float, player_move: Dict) -> None:
        if player_move is not None and player_move['source_tile'] != tile and player_move['target_tile'] != tile:
            return

        from game import Game

        if tile in self.game_map_tiles:
            game_map_tile = self.game_map_tiles[tile]
        else:
            game_map_tile = None

        tile_owner_id = self.game.get_tile_owner(tile)
        tile_owner = self.game.get_player(tile_owner_id)
        troop_count = self.game.get_tile_troops(tile)
        tile_alpha = max(0.5, troop_count / Game.TileTroopMax)
        tile_color = tile_owner.tile_color

        if game_map_tile:
            if game_map_tile.tile_background.get_alpha() != tile_alpha:
                game_map_tile.tile_background.set_alpha(tile_alpha)

            if game_map_tile.tile_background.get_facecolor() != tile_color:
                game_map_tile.tile_background.set_facecolor(tile_color)
        else:
            tile_background = self.axis.add_patch(
                RegularPolygon(
                    xy=poly_xy,
                    numVertices=6,
                    radius=0.8,
                    alpha=tile_alpha,
                    facecolor=tile_owner.tile_color)
            )

        troop_value = str(troop_count)
        troop_visibility = troop_count > 0

        if game_map_tile:
            if game_map_tile.troops_text.get_text() != troop_value:
                game_map_tile.troops_text.set_text(troop_value)

            if game_map_tile.troops_text.get_visible() != troop_visibility:
                game_map_tile.troops_text.set_visible(troop_visibility)
        else:
            troops_text = self.axis.text(
                x=poly_xy[0],
                y=poly_xy[1] + 0.2,
                s=str(troop_count),
                fontsize='medium',
                color='#18181B',
                horizontalalignment='center',
                verticalalignment='center'
            )

            troops_text.set_visible(troop_visibility)

        tile_coords_value = str(tile)

        if game_map_tile:
            if game_map_tile.tile_coords_text.get_text() != tile_coords_value:
                game_map_tile.tile_coords_text.set_text(tile_coords_value)
        else:
            tile_coords_text = self.axis.text(
                x=poly_xy[0],
                y=poly_xy[1] - 0.1,
                s=str(tile),
                alpha=0.3,
                fontsize='x-small',
                color='#18181B',
                horizontalalignment='center',
                verticalalignment='center'
            )

        if game_map_tile:
            game_map_tile.encoding_value_text.set_text(str(encoding_value))
        else:
            encoding_value_text = self.axis.text(
                x=poly_xy[0],
                y=poly_xy[1] - 0.4,
                s=str(encoding_value),
                alpha=0.3,
                fontsize='x-small',
                color='#18181B',
                horizontalalignment='center',
                verticalalignment='center'
            )

        if not game_map_tile:
            self.game_map_tiles[tile] = GameMapTile(
                tile_background,
                troops_text,
                tile_coords_text,
                encoding_value_text
            )

    def render(self, title: str = None, subtitle: str = None, player_move: Dict = None, show=True) -> None:
        if show:
            plt.ion()
            plt.show()

        if self.figure is None:
            plt.close()
            self.figure, self.axis = plt.subplots()  # type: Figure, Axes

        if player_move is None:
            self.axis.cla()
            self.game_map_tiles = defaultdict(list)

        plt.setp(self.axis.get_xticklabels(), visible=False)
        plt.setp(self.axis.get_yticklabels(), visible=False)
        self.axis.tick_params(axis='both', which='both', length=0)
        self.axis.set_aspect('equal')
        self.axis.set_xticks(range(1, 11))
        self.axis.set_yticks(range(1, 9))

        title = title or self.create_title(player_move)
        subtitle = subtitle or self.create_subtitle()
        self.figure.suptitle(title)
        self.axis.set_title(subtitle)

        state = self.game.state_parser.encode_state()

        self.render_tile((0, 0), (1.0, 7.0), state[0], player_move)
        self.render_tile((0, 1), (2.4, 7.0), state[1], player_move)
        self.render_tile((0, 2), (3.8, 7.0), state[2], player_move)
        self.render_tile((0, 3), (5.2, 7.0), state[3], player_move)
        self.render_tile((0, 4), (6.6, 7.0), state[4], player_move)
        self.render_tile((0, 5), (8.0, 7.0), state[5], player_move)

        self.render_tile((1, 0), (1.7, 5.8), state[6], player_move)
        self.render_tile((1, 1), (3.1, 5.8), state[7], player_move)
        self.render_tile((1, 2), (4.5, 5.8), state[8], player_move)
        self.render_tile((1, 3), (5.9, 5.8), state[9], player_move)
        self.render_tile((1, 4), (7.3, 5.8), state[10], player_move)
        self.render_tile((1, 5), (8.7, 5.8), state[11], player_move)

        self.render_tile((2, 0), (1.0, 4.6), state[12], player_move)
        self.render_tile((2, 1), (2.4, 4.6), state[13], player_move)
        self.render_tile((2, 2), (3.8, 4.6), state[14], player_move)
        self.render_tile((2, 3), (5.2, 4.6), state[15], player_move)
        self.render_tile((2, 4), (6.6, 4.6), state[16], player_move)
        self.render_tile((2, 5), (8.0, 4.6), state[17], player_move)

        self.render_tile((3, 0), (1.7, 3.4), state[18], player_move)
        self.render_tile((3, 1), (3.1, 3.4), state[19], player_move)
        self.render_tile((3, 2), (4.5, 3.4), state[20], player_move)
        self.render_tile((3, 3), (5.9, 3.4), state[21], player_move)
        self.render_tile((3, 4), (7.3, 3.4), state[22], player_move)
        self.render_tile((3, 5), (8.7, 3.4), state[23], player_move)

        self.render_tile((4, 0), (1.0, 2.2), state[24], player_move)
        self.render_tile((4, 1), (2.4, 2.2), state[25], player_move)
        self.render_tile((4, 2), (3.8, 2.2), state[26], player_move)
        self.render_tile((4, 3), (5.2, 2.2), state[27], player_move)
        self.render_tile((4, 4), (6.6, 2.2), state[28], player_move)
        self.render_tile((4, 5), (8.0, 2.2), state[29], player_move)

        self.render_tile((5, 0), (1.7, 1.0), state[30], player_move)
        self.render_tile((5, 1), (3.1, 1.0), state[31], player_move)
        self.render_tile((5, 2), (4.5, 1.0), state[32], player_move)
        self.render_tile((5, 3), (5.9, 1.0), state[33], player_move)
        self.render_tile((5, 4), (7.3, 1.0), state[34], player_move)
        self.render_tile((5, 5), (8.7, 1.0), state[35], player_move)

        if show:
            plt.pause(0.001)

    def save(self, player_move: Dict = None, render: bool = True) -> None:

        if not os.path.isdir(self.save_path):
            os.mkdir(self.save_path)

        rounds = self.game.rounds
        player_id = self.game.player_id

        if rounds == 0:
            game_file = f'round-{rounds}-start'
        else:
            game_file = f'round-{rounds}-player-{player_id}'

        if render:
            self.render(player_move=player_move, show=False)

        self.figure.savefig(f'{self.save_path}/{game_file}.png')
