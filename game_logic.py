"""
Core game logic for Minesweeper.
"""

import random
from typing import List, Set, Tuple, Optional
from collections import deque

from models import Cell, Position, GameState, CellState, GameStats
from constants import MINE_VALUE, EMPTY_CELL, GameConfig


class GameLogicError(Exception):
    """Custom exception for game logic errors."""
    pass


class MinesweeperGame:
    """Core game logic for Minesweeper."""
    
    def __init__(self, config: GameConfig):
        """Initialize a new game with given configuration."""
        self.config = config
        self.grid: List[List[Cell]] = []
        self.game_state = GameState.PLAYING
        self.first_click = True
        self.stats = GameStats(
            remaining_mines=config.mines,
            revealed_cells=0,
            total_cells=config.rows * config.cols,
            flagged_cells=0
        )
        self._initialize_grid()
    
    def _initialize_grid(self) -> None:
        """Initialize the game grid with empty cells."""
        self.grid = [
            [Cell() for _ in range(self.config.cols)]
            for _ in range(self.config.rows)
        ]
    
    def _is_valid_position(self, pos: Position) -> bool:
        """Check if position is within grid bounds."""
        return (0 <= pos.row < self.config.rows and 
                0 <= pos.col < self.config.cols)
    
    def _place_mines(self, exclude_pos: Position) -> None:
        """Place mines randomly on the grid, excluding the first clicked position."""
        # Get all possible positions except the first clicked one and its neighbors
        exclude_positions = {exclude_pos}
        exclude_positions.update(exclude_pos.get_neighbors(self.config.rows, self.config.cols))
        
        available_positions = []
        for row in range(self.config.rows):
            for col in range(self.config.cols):
                pos = Position(row, col)
                if pos not in exclude_positions:
                    available_positions.append(pos)
        
        if len(available_positions) < self.config.mines:
            raise GameLogicError("Not enough positions to place all mines")
        
        # Randomly select mine positions
        mine_positions = random.sample(available_positions, self.config.mines)
        
        # Place mines and update adjacent cell counts
        for pos in mine_positions:
            self.grid[pos.row][pos.col].value = MINE_VALUE
            self._update_adjacent_counts(pos)
    
    def _update_adjacent_counts(self, mine_pos: Position) -> None:
        """Update the count of adjacent mines for cells around a mine."""
        neighbors = mine_pos.get_neighbors(self.config.rows, self.config.cols)
        for neighbor in neighbors:
            cell = self.grid[neighbor.row][neighbor.col]
            if not cell.is_mine:
                cell.value += 1
    
    def _reveal_empty_area(self, start_pos: Position) -> Set[Position]:
        """Reveal all connected empty cells using BFS."""
        revealed = set()
        queue = deque([start_pos])
        
        while queue:
            pos = queue.popleft()
            if pos in revealed:
                continue
                
            cell = self.grid[pos.row][pos.col]
            if cell.is_revealed or cell.is_flagged:
                continue
                
            cell.reveal()
            revealed.add(pos)
            self.stats.revealed_cells += 1
            
            # If it's an empty cell, add neighbors to queue
            if cell.value == EMPTY_CELL:
                neighbors = pos.get_neighbors(self.config.rows, self.config.cols)
                for neighbor in neighbors:
                    if neighbor not in revealed:
                        queue.append(neighbor)
        
        return revealed
    
    def left_click(self, pos: Position) -> Set[Position]:
        """Handle left click on a cell. Returns set of positions that were revealed."""
        if not self._is_valid_position(pos):
            raise GameLogicError(f"Invalid position: {pos}")
        
        if self.game_state != GameState.PLAYING:
            return set()
        
        cell = self.grid[pos.row][pos.col]
        
        # Can't click on flagged cells
        if cell.is_flagged:
            return set()
        
        # Handle first click
        if self.first_click:
            self._place_mines(pos)
            self.first_click = False
        
        # If already revealed, try chord clicking
        if cell.is_revealed:
            return self._chord_click(pos)
        
        # Reveal the cell
        revealed_positions = set()
        
        if cell.is_mine:
            # Game over
            cell.reveal()
            self.game_state = GameState.LOST
            revealed_positions.add(pos)
        elif cell.value == EMPTY_CELL:
            # Reveal connected empty area
            revealed_positions = self._reveal_empty_area(pos)
        else:
            # Reveal single numbered cell
            cell.reveal()
            self.stats.revealed_cells += 1
            revealed_positions.add(pos)
        
        # Check win condition
        self._check_win_condition()
        
        return revealed_positions
    
    def right_click(self, pos: Position) -> bool:
        """Handle right click (flag/unflag). Returns True if mine count changed."""
        if not self._is_valid_position(pos):
            raise GameLogicError(f"Invalid position: {pos}")
        
        if self.game_state != GameState.PLAYING:
            return False
        
        cell = self.grid[pos.row][pos.col]
        
        # Can't flag revealed cells
        if cell.is_revealed:
            return False
        
        was_flagged = cell.is_flagged
        cell.toggle_flag()
        
        if was_flagged:
            self.stats.remaining_mines += 1
            self.stats.flagged_cells -= 1
        else:
            self.stats.remaining_mines -= 1
            self.stats.flagged_cells += 1
        
        return True
    
    def _chord_click(self, pos: Position) -> Set[Position]:
        """Handle chord clicking (reveal adjacent cells if enough flags)."""
        cell = self.grid[pos.row][pos.col]
        if not cell.is_revealed or cell.value <= 0:
            return set()
        
        neighbors = pos.get_neighbors(self.config.rows, self.config.cols)
        flagged_count = sum(1 for n in neighbors if self.grid[n.row][n.col].is_flagged)
        
        # Only chord if flagged count matches the cell's number
        if flagged_count != cell.value:
            return set()
        
        revealed_positions = set()
        for neighbor in neighbors:
            neighbor_cell = self.grid[neighbor.row][neighbor.col]
            if not neighbor_cell.is_revealed and not neighbor_cell.is_flagged:
                revealed_positions.update(self.left_click(neighbor))
        
        return revealed_positions
    
    def _check_win_condition(self) -> None:
        """Check if the player has won the game."""
        if self.game_state != GameState.PLAYING:
            return
        
        # Win if all non-mine cells are revealed
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return
        
        self.game_state = GameState.WON
    
    def reveal_all_mines(self) -> List[Position]:
        """Reveal all mines (used when game is lost). Returns positions of all mines."""
        mine_positions = []
        for row in range(self.config.rows):
            for col in range(self.config.cols):
                cell = self.grid[row][col]
                if cell.is_mine:
                    cell.reveal()
                    mine_positions.append(Position(row, col))
        return mine_positions
    
    def get_cell(self, pos: Position) -> Cell:
        """Get cell at given position."""
        if not self._is_valid_position(pos):
            raise GameLogicError(f"Invalid position: {pos}")
        return self.grid[pos.row][pos.col]
    
    def is_game_over(self) -> bool:
        """Check if game is over (won or lost)."""
        return self.game_state in (GameState.WON, GameState.LOST)
    
    def is_won(self) -> bool:
        """Check if game is won."""
        return self.game_state == GameState.WON
    
    def is_lost(self) -> bool:
        """Check if game is lost."""
        return self.game_state == GameState.LOST
