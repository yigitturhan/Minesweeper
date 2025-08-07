"""
Data models for the Minesweeper game.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Set


class CellState(Enum):
    """Possible states of a cell."""
    HIDDEN = "hidden"
    REVEALED = "revealed"
    FLAGGED = "flagged"


class GameState(Enum):
    """Possible game states."""
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


@dataclass
class Cell:
    """Represents a single cell in the minesweeper grid."""
    value: int = 0  # Number of adjacent mines, or MINE_VALUE if it's a mine
    state: CellState = CellState.HIDDEN
    
    @property
    def is_mine(self) -> bool:
        """Check if this cell contains a mine."""
        from constants import MINE_VALUE
        return self.value == MINE_VALUE
    
    @property
    def is_revealed(self) -> bool:
        """Check if this cell is revealed."""
        return self.state == CellState.REVEALED
    
    @property
    def is_flagged(self) -> bool:
        """Check if this cell is flagged."""
        return self.state == CellState.FLAGGED
    
    @property
    def is_hidden(self) -> bool:
        """Check if this cell is hidden."""
        return self.state == CellState.HIDDEN
    
    def reveal(self) -> None:
        """Reveal this cell."""
        if self.state != CellState.FLAGGED:
            self.state = CellState.REVEALED
    
    def toggle_flag(self) -> bool:
        """Toggle flag state. Returns True if flagged, False if unflagged."""
        if self.state == CellState.HIDDEN:
            self.state = CellState.FLAGGED
            return True
        elif self.state == CellState.FLAGGED:
            self.state = CellState.HIDDEN
            return False
        return self.is_flagged


@dataclass
class Position:
    """Represents a position in the grid."""
    row: int
    col: int
    
    def __hash__(self) -> int:
        return hash((self.row, self.col))
    
    def get_neighbors(self, max_row: int, max_col: int) -> List['Position']:
        """Get all valid neighboring positions."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = self.row + dr, self.col + dc
                if 0 <= new_row < max_row and 0 <= new_col < max_col:
                    neighbors.append(Position(new_row, new_col))
        return neighbors


@dataclass
class GameStats:
    """Statistics for the current game."""
    remaining_mines: int
    revealed_cells: int
    total_cells: int
    flagged_cells: int
    
    @property
    def cells_to_reveal(self) -> int:
        """Number of cells still needed to be revealed to win."""
        return self.total_cells - self.remaining_mines - self.revealed_cells
