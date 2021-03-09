import random

from game import Game
from game_map import GameMap
from state_parser import StateParser


def main():
    game = Game()
    state_parser = StateParser(game)
    game_map = GameMap(game, state_parser)
    game_map.set_players('Blue R', 'Red R')
    game_map.render()

    while True:
        game.set_player_id(Game.BluePlayer)
        blue_move = random.choice(get_next_moves(game))
        apply_move(game, blue_move)

        game_map.set_player_move(blue_move)
        game_map.render()

        if game.has_ended():
            break

        game.set_player_id(Game.RedPlayer)
        red_move = random.choice(get_next_moves(game))
        apply_move(game, red_move)

        game_map.set_player_move(red_move)
        game_map.render()

        if game.has_ended():
            break

        game.increase_round()


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
