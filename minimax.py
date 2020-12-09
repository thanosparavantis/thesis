import math
import random

from Game import Game
from GameMap import GameMap
from StateParser import StateParser


def main():
    game = Game()
    state_parser = StateParser(game)
    game_map = GameMap(game, state_parser)

    game_map.render()

    while not game.has_ended():
        next_moves = get_next_moves(game)
        random.shuffle(next_moves)
        maximizing_player = True if game.get_player_id() == Game.BluePlayer else False
        next_move, evaluation = minimax(game, 3, maximizing_player)
        apply_move(game, next_move)
        game_map.set_player_move(next_move)
        game_map.render()
        game.change_player_id()

    game_map.render()


def minimax(game, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
    if depth == 0 or game.has_ended():
        fitness = get_fitness(game)
        return None, fitness

    if maximizing_player:
        maxEval = -math.inf
        best_move = None

        for move in get_next_moves(game):
            undo_move = Game.copy_of(game)
            apply_move(game, move)
            game.set_player_id(Game.RedPlayer)
            next_move, evaluation = minimax(game, depth - 1, False, alpha, beta)
            game = undo_move

            if maxEval < evaluation:
                maxEval = max(maxEval, evaluation)
                best_move = next_move

            alpha = max(alpha, evaluation)

            if beta <= alpha:
                break

        return best_move, maxEval
    else:
        minEval = math.inf
        best_move = None

        for move in get_next_moves(game):
            undo_move = Game.copy_of(game)
            apply_move(game, move)
            game.set_player_id(Game.BluePlayer)
            next_move, evaluation = minimax(game, depth - 1, True, alpha, beta)
            game = undo_move

            if minEval > evaluation:
                minEval = min(minEval, evaluation)
                best_move = move

            beta = min(beta, evaluation)

            if beta <= alpha:
                break

        return best_move, minEval


def apply_temp_move(game, move):
    temp_game = Game.copy_of(game)
    return apply_move(temp_game, move)


def apply_move(game, move):
    move_type = move['move_type']
    source_tile = move['source_tile']
    target_tile = move['target_tile']
    troops = move['troops']

    if move_type == Game.ProductionMove:
        game.production_move(source_tile)
    elif move_type == Game.AttackMove:
        game.attack_move(source_tile, target_tile, troops)
    elif move_type == Game.TransportMove:
        game.transport_move(source_tile, target_tile, troops)

    return game


def get_fitness(game):
    blue_tile_count = game.get_tile_count(Game.BluePlayer)
    red_tile_count = game.get_tile_count(Game.RedPlayer)
    blue_troop_count = game.get_troop_count(Game.BluePlayer)
    red_troop_count = game.get_troop_count(Game.RedPlayer)

    return ((blue_tile_count - red_tile_count) / Game.MapSize) + ((blue_troop_count - red_troop_count) / (Game.MapSize * Game.TileTroopMax))


def get_next_moves(game: Game):
    next_states = []
    player_id = game.get_player_id()
    tiles = game.get_tiles(player_id)

    for tile in tiles:
        tile_troops = game.get_tile_troops(tile)

        if tile_troops + 1 <= Game.TileTroopMax:
            next_states.append({
                'move_type': Game.ProductionMove,
                'source_tile': tile,
                'target_tile': None,
                'troops': None,
            })

        for tile_adj in game.get_tile_adj(tile):
            tile_adj_troops = game.get_tile_troops(tile_adj)

            if tile_adj not in tiles:
                for troops in range(Game.TileTroopMin, tile_troops + 1):
                    next_states.append({
                        'move_type': Game.AttackMove,
                        'source_tile': tile,
                        'target_tile': tile_adj,
                        'troops': troops,
                    })

            if tile_adj in tiles:
                for troops in range(Game.TileTroopMin, min(Game.TileTroopMax - tile_adj_troops, tile_troops) + 1):
                    next_states.append({
                        'move_type': Game.TransportMove,
                        'source_tile': tile,
                        'target_tile': tile_adj,
                        'troops': troops,
                    })

    return next_states


if __name__ == '__main__':
    main()
