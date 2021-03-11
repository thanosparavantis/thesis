from matplotlib.patches import RegularPolygon
from matplotlib.text import Text


class GameMapTile:
    def __init__(self,
                 tile_background: RegularPolygon,
                 troops_text: Text,
                 tile_coords_text: Text,
                 encoding_value_text: Text):
        self.tile_background = tile_background
        self.troops_text = troops_text
        self.tile_coords_text = tile_coords_text
        self.encoding_value_text = encoding_value_text
