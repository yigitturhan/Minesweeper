"""
Constants for the Minesweeper game.
"""

from enum import Enum
from typing import NamedTuple


class Difficulty(Enum):
    """Game difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class GameConfig(NamedTuple):
    """Configuration for a game difficulty."""
    rows: int
    cols: int
    mines: int


# Game configurations
GAME_CONFIGS = {
    Difficulty.BEGINNER: GameConfig(9, 9, 10),
    Difficulty.INTERMEDIATE: GameConfig(16, 16, 40),
    Difficulty.EXPERT: GameConfig(30, 16, 99),
}

# Game constants
MINE_VALUE = -1  # Changed from 9 to -1 for clarity
EMPTY_CELL = 0

# UI constants
CELL_WIDTH = 4
CELL_HEIGHT = 2
IMAGE_SIZE = (35, 33)

# Colors for numbers
COLOR_MAPPING = {
    1: 'blue',
    2: 'green',
    3: 'brown',
    4: 'purple',
    5: 'red',
    6: 'cyan',
    7: 'orange',
    8: 'black'
}

# UI colors
BG_COLOR = 'grey81'
OPENED_BG_COLOR = 'grey60'
MINE_BG_COLOR = 'red'

# Mouse buttons
LEFT_CLICK = "<Button-1>"
RIGHT_CLICK = "<Button-3>"  # Changed from Button-2 to Button-3 for right click
MIDDLE_CLICK = "<Button-2>"

# Window settings
WINDOW_TITLE = "Minesweeper"
FONT_LARGE = ("Helvetica", 24)
FONT_NORMAL = ("Helvetica", 12)

# Asset paths
BOMB_IMAGE_PATH = "assets/bomb.png"
FLAG_IMAGE_PATH = "assets/flag.png"
