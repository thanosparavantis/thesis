import json
from operator import attrgetter

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from game import Game
from game_result import GameResult
from shared import get_folder_contents, print_signature


def main():
    print_signature("Training Statistics")

    gs_files = get_folder_contents(f'game-results')

    fit_data = []
    tile_data = []
    troop_data = []
    prod_data = []
    att_data = []
    trans_data = []
    round_data = []
    win_data = []
    guided_data = []

    for filename in gs_files:
        file = open(f'game-results/{filename}', 'r')
        game_results = json.load(file)
        file.close()

        game_results = [GameResult(game_json=game_json) for game_json in game_results]

        fit_data.append((
            max(game_results, key=attrgetter('blue_fitness')).blue_fitness,
            max(game_results, key=attrgetter('red_fitness')).red_fitness,
            np.mean([gs.blue_fitness for gs in game_results]),
            np.mean([gs.red_fitness for gs in game_results])
        ))

        tile_data.append((
            np.mean([gs.blue_tiles for gs in game_results]),
            np.mean([Game.MapSize - (gs.blue_tiles + gs.red_tiles) for gs in game_results]),
            np.mean([gs.red_tiles for gs in game_results])
        ))

        troop_data.append((
            np.mean([gs.blue_troops for gs in game_results]),
            np.mean([gs.red_troops for gs in game_results])
        ))

        prod_data.append((
            np.mean([gs.blue_production_moves for gs in game_results]),
            np.mean([gs.red_production_moves for gs in game_results])
        ))

        att_data.append((
            np.mean([gs.blue_attack_moves for gs in game_results]),
            np.mean([gs.red_attack_moves for gs in game_results])
        ))

        trans_data.append((
            np.mean([gs.blue_transport_moves for gs in game_results]),
            np.mean([gs.red_transport_moves for gs in game_results])
        ))

        round_data.append(np.mean([gs.rounds for gs in game_results]))

        win_data.append((
            len(list(filter(lambda gs: gs.winner == 'Blue', game_results))),
            len(list(filter(lambda gs: gs.winner == 'Tie', game_results))),
            len(list(filter(lambda gs: gs.winner == 'Red', game_results)))
        ))

        guided_data.append((
            np.mean([gs.blue_guided_moves for gs in game_results]),
            np.mean([gs.red_guided_moves for gs in game_results])
        ))

    fig, axes = plt.subplots(3, 3)  # type: Figure, Axes

    fig.suptitle('Game results per generation')

    fit_ax = axes[0][0]  # type: Axes
    fit_ax.plot([fitness[0] for fitness in fit_data], color='#2563EB')
    fit_ax.plot([fitness[1] for fitness in fit_data], color='#DC2626')
    fit_ax.plot([fitness[2] for fitness in fit_data], color='#2563EB', alpha=0.5)
    fit_ax.plot([fitness[3] for fitness in fit_data], color='#DC2626', alpha=0.5)
    fit_ax.set_title('Fitness')

    tile_ax = axes[0][1]  # type: Axes
    tile_ax.plot([tiles[0] for tiles in tile_data], color='#2563EB')
    tile_ax.plot([tiles[1] for tiles in tile_data], color='#71717A')
    tile_ax.plot([tiles[2] for tiles in tile_data], color='#DC2626')
    tile_ax.set_title('Tiles')

    troop_ax = axes[0][2]  # type: Axes
    troop_ax.plot([troops[0] for troops in troop_data], color='#2563EB')
    troop_ax.plot([troops[1] for troops in troop_data], color='#DC2626')
    troop_ax.set_title('Troops')

    prod_ax = axes[1][0]  # type: Axes
    prod_ax.plot([prod[0] for prod in prod_data], color='#2563EB')
    prod_ax.plot([prod[1] for prod in prod_data], color='#DC2626')
    prod_ax.set_title('Production')

    att_ax = axes[1][1]  # type: Axes
    att_ax.plot([att[0] for att in att_data], color='#2563EB')
    att_ax.plot([att[1] for att in att_data], color='#DC2626')
    att_ax.set_title('Attacks')

    trans_ax = axes[1][2]  # type: Axes
    trans_ax.plot([trans[0] for trans in trans_data], color='#2563EB')
    trans_ax.plot([trans[1] for trans in trans_data], color='#DC2626')
    trans_ax.set_title('Transports')

    rounds_ax = axes[2][0]  # type: Axes
    rounds_ax.plot([rounds for rounds in round_data], color='#0EA5E9')
    rounds_ax.set_title('Rounds')

    win_ax = axes[2][1]  # type: Axes
    win_ax.plot([winners[0] for winners in win_data], color='#2563EB')
    win_ax.plot([winners[1] for winners in win_data], color='#71717A')
    win_ax.plot([winners[2] for winners in win_data], color='#DC2626')
    win_ax.set_title('Wins')

    guided_ax = axes[2][2]  # type: Axes
    guided_ax.plot([guided[0] for guided in guided_data], color='#2563EB')
    guided_ax.plot([guided[1] for guided in guided_data], color='#DC2626')
    guided_ax.set_title('Guidance')

    plt.show()


if __name__ == '__main__':
    main()
