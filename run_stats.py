import json
from operator import attrgetter
from typing import List, Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from game_result import GameResult
from shared import get_folder_contents, print_signature, parse_args


def main():
    print_signature("Training Statistics")

    args = parse_args("Plot fitness, tiles, troops, production, attacks, transports, rounds and winners through generations.")

    preset = args.preset

    gs_files = get_folder_contents(f'./game-results-{preset}')  # type: List[str]

    gs_data = []  # type: List[GameResult]
    win_data = []  # type: List[Tuple[int, int, int]]

    for filename in gs_files:
        file = open(f'./game-results-{preset}/{filename}', 'r')
        game_results = json.load(file)
        file.close()
        game_results = [GameResult(game_json=game_json) for game_json in game_results]
        blue_wins = len(list(filter(lambda gs: gs.winner == 'Blue', game_results)))
        ties = len(list(filter(lambda gs: gs.winner == 'Tie', game_results)))
        red_wins = len(list(filter(lambda gs: gs.winner == 'Red', game_results)))
        gs_best = max(game_results, key=attrgetter('fitness'))
        gs_data.append(gs_best)
        win_data.append((blue_wins, ties, red_wins))

    fig, axes = plt.subplots(3, 3)  # type: Figure, Axes

    fig.suptitle('Game results per generation')

    fit_ax = axes[0][0]  # type: Axes
    fit_ax.plot([gs.fitness for gs in gs_data], color='#10B981')
    fit_ax.set_title('Fitness')

    tile_ax = axes[0][1]  # type: Axes
    tile_ax.plot([gs.blue_tiles for gs in gs_data], color='#2563EB')
    tile_ax.plot([gs.red_tiles for gs in gs_data], color='#DC2626')
    tile_ax.set_title('Tiles')

    troop_ax = axes[0][2]  # type: Axes
    troop_ax.plot([gs.blue_troops for gs in gs_data], color='#2563EB')
    troop_ax.plot([gs.red_troops for gs in gs_data], color='#DC2626')
    troop_ax.set_title('Troops')

    prod_ax = axes[1][0]  # type: Axes
    prod_ax.plot([gs.blue_production_moves for gs in gs_data], color='#2563EB')
    prod_ax.plot([gs.red_production_moves for gs in gs_data], color='#DC2626')
    prod_ax.set_title('Production')

    att_ax = axes[1][1]  # type: Axes
    att_ax.plot([gs.blue_attack_moves for gs in gs_data], color='#2563EB')
    att_ax.plot([gs.red_attack_moves for gs in gs_data], color='#DC2626')
    att_ax.set_title('Attacks')

    trans_ax = axes[1][2]  # type: Axes
    trans_ax.plot([gs.blue_transport_moves for gs in gs_data], color='#2563EB')
    trans_ax.plot([gs.red_transport_moves for gs in gs_data], color='#DC2626')
    trans_ax.set_title('Transports')

    rounds_ax = axes[2][0]  # type: Axes
    rounds_ax.plot([gs.rounds for gs in gs_data], color='#0EA5E9')
    rounds_ax.set_title('Rounds')

    win_ax = axes[2][1]  # type: Axes
    win_ax.plot([winners[0] for winners in win_data], color='#2563EB')
    win_ax.plot([winners[1] for winners in win_data], color='#71717A')
    win_ax.plot([winners[2] for winners in win_data], color='#DC2626')
    win_ax.set_title('Winner')

    plt.show()


if __name__ == '__main__':
    main()
