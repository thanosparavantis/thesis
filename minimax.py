import math
import random
import signal
import time

from game import Game
from game_map import GameMap
from state_parser import StateParser
from zobrist_hashing import ZobristHashing


def main():
    zobrist = ZobristHashing()

    signal.signal(signal.SIGINT, lambda sig, frame: zobrist.save_data())

    game = Game()
    state_parser = StateParser(game)
    game_map = GameMap(game, state_parser)
    game_map.render()

    moves = []

    while not game.has_ended():
        maximizing_player = True if game.get_player_id() == Game.BluePlayer else False
        next_move, evaluation = minimax(game, zobrist, 1, maximizing_player)
        moves.append(next_move)
        apply_move(game, next_move)

        game_map.set_player_move(next_move)
        game_map.render()

        game.change_player_id()

        if game.get_player_id() == Game.BluePlayer:
            game.increase_round()


def minimax(game, zobrist, depth, maximizing_player, alpha=-math.inf, beta=math.inf):
    if depth == 0 or game.has_ended():
        blue_fitness, red_fitness = game.get_fitness()
        fitness = blue_fitness - red_fitness
        return None, fitness

    if maximizing_player:
        max_eval = -math.inf
        blue_move = None

        for move in get_next_moves(game):
            temp_game = apply_temp_move(game, Game.RedPlayer, move)
            game_hash = zobrist.get_game_hash(temp_game)

            if zobrist.has_data(game_hash):
                evaluation = zobrist.get_data(game_hash)
            else:
                next_move, evaluation = minimax(temp_game, zobrist, depth - 1, False, alpha, beta)
                zobrist.store_data(game_hash, evaluation)

            if max_eval < evaluation:
                max_eval = max(max_eval, evaluation)
                blue_move = move

            alpha = max(alpha, evaluation)

            if beta <= alpha:
                break

        return blue_move, max_eval
    else:
        min_eval = math.inf
        red_move = None

        for move in get_next_moves(game):
            temp_game = apply_temp_move(game, Game.BluePlayer, move)
            game_hash = zobrist.get_game_hash(temp_game)

            if zobrist.has_data(game_hash):
                evaluation = zobrist.get_data(game_hash)
            else:
                next_move, evaluation = minimax(temp_game, zobrist, depth - 1, True, alpha, beta)
                zobrist.store_data(game_hash, evaluation)

            if min_eval > evaluation:
                min_eval = min(min_eval, evaluation)
                red_move = move

            beta = min(beta, evaluation)

            if beta <= alpha:
                break

        return red_move, min_eval


def apply_temp_move(game, player_id, move):
    temp_game = Game.copy_of(game)
    apply_move(temp_game, move)
    temp_game.set_player_id(player_id)
    return temp_game


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

    random.shuffle(next_states)
    return next_states


if __name__ == '__main__':
    main()
