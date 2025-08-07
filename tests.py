"""
Unit tests for the Minesweeper game.
"""

import unittest
from unittest.mock import patch
import random

from constants import MINE_VALUE, EMPTY_CELL, GameConfig
from models import Cell, Position, CellState, GameState
from game_logic import MinesweeperGame, GameLogicError


class TestCell(unittest.TestCase):
    """Test cases for Cell model."""
    
    def setUp(self):
        self.cell = Cell()
    
    def test_initial_state(self):
        """Test cell initial state."""
        self.assertEqual(self.cell.value, 0)
        self.assertEqual(self.cell.state, CellState.HIDDEN)
        self.assertFalse(self.cell.is_mine)
        self.assertFalse(self.cell.is_revealed)
        self.assertFalse(self.cell.is_flagged)
        self.assertTrue(self.cell.is_hidden)
    
    def test_mine_cell(self):
        """Test mine cell properties."""
        mine_cell = Cell(value=MINE_VALUE)
        self.assertTrue(mine_cell.is_mine)
    
    def test_reveal_cell(self):
        """Test cell reveal functionality."""
        self.cell.reveal()
        self.assertTrue(self.cell.is_revealed)
        self.assertEqual(self.cell.state, CellState.REVEALED)
    
    def test_flag_toggle(self):
        """Test flag toggle functionality."""
        # Flag the cell
        result = self.cell.toggle_flag()
        self.assertTrue(result)
        self.assertTrue(self.cell.is_flagged)
        
        # Unflag the cell
        result = self.cell.toggle_flag()
        self.assertFalse(result)
        self.assertFalse(self.cell.is_flagged)
        self.assertTrue(self.cell.is_hidden)
    
    def test_cannot_flag_revealed_cell(self):
        """Test that revealed cells cannot be flagged."""
        self.cell.reveal()
        result = self.cell.toggle_flag()
        self.assertFalse(result)
        self.assertFalse(self.cell.is_flagged)


class TestPosition(unittest.TestCase):
    """Test cases for Position model."""
    
    def test_position_creation(self):
        """Test position creation."""
        pos = Position(3, 4)
        self.assertEqual(pos.row, 3)
        self.assertEqual(pos.col, 4)
    
    def test_position_hash(self):
        """Test position hashing."""
        pos1 = Position(3, 4)
        pos2 = Position(3, 4)
        pos3 = Position(4, 3)
        
        self.assertEqual(hash(pos1), hash(pos2))
        self.assertNotEqual(hash(pos1), hash(pos3))
    
    def test_get_neighbors(self):
        """Test neighbor calculation."""
        pos = Position(1, 1)
        neighbors = pos.get_neighbors(3, 3)
        
        expected_neighbors = [
            Position(0, 0), Position(0, 1), Position(0, 2),
            Position(1, 0),                  Position(1, 2),
            Position(2, 0), Position(2, 1), Position(2, 2)
        ]
        
        self.assertEqual(len(neighbors), 8)
        for expected in expected_neighbors:
            self.assertIn(expected, neighbors)
    
    def test_get_neighbors_corner(self):
        """Test neighbor calculation for corner position."""
        pos = Position(0, 0)
        neighbors = pos.get_neighbors(3, 3)
        
        expected_neighbors = [
            Position(0, 1), Position(1, 0), Position(1, 1)
        ]
        
        self.assertEqual(len(neighbors), 3)
        for expected in expected_neighbors:
            self.assertIn(expected, neighbors)


class TestMinesweeperGame(unittest.TestCase):
    """Test cases for MinesweeperGame."""
    
    def setUp(self):
        """Set up test game."""
        self.config = GameConfig(5, 5, 3)
        self.game = MinesweeperGame(self.config)
    
    def test_initial_state(self):
        """Test game initial state."""
        self.assertEqual(self.game.config, self.config)
        self.assertEqual(self.game.game_state, GameState.PLAYING)
        self.assertTrue(self.game.first_click)
        self.assertEqual(self.game.stats.remaining_mines, 3)
        self.assertEqual(self.game.stats.revealed_cells, 0)
        self.assertEqual(self.game.stats.total_cells, 25)
        self.assertEqual(len(self.game.grid), 5)
        self.assertEqual(len(self.game.grid[0]), 5)
    
    def test_invalid_position(self):
        """Test handling of invalid positions."""
        with self.assertRaises(GameLogicError):
            self.game.left_click(Position(-1, 0))
        
        with self.assertRaises(GameLogicError):
            self.game.left_click(Position(5, 5))
    
    @patch('random.sample')
    def test_mine_placement(self, mock_sample):
        """Test mine placement logic."""
        # Mock mine positions
        mock_sample.return_value = [Position(2, 2), Position(3, 3), Position(4, 4)]
        
        # First click should place mines
        self.game.left_click(Position(0, 0))
        
        # Check that mines were placed
        mine_count = 0
        for row in self.game.grid:
            for cell in row:
                if cell.is_mine:
                    mine_count += 1
        
        self.assertEqual(mine_count, 3)
        self.assertFalse(self.game.first_click)
    
    def test_flag_functionality(self):
        """Test flag functionality."""
        pos = Position(0, 0)
        
        # Flag cell
        result = self.game.right_click(pos)
        self.assertTrue(result)
        self.assertEqual(self.game.stats.remaining_mines, 2)
        self.assertEqual(self.game.stats.flagged_cells, 1)
        
        # Unflag cell
        result = self.game.right_click(pos)
        self.assertTrue(result)
        self.assertEqual(self.game.stats.remaining_mines, 3)
        self.assertEqual(self.game.stats.flagged_cells, 0)
    
    def test_cannot_flag_revealed_cell(self):
        """Test that revealed cells cannot be flagged."""
        pos = Position(0, 0)
        
        # Reveal cell first
        self.game.left_click(pos)  # This will place mines and reveal
        
        # Try to flag revealed cell
        result = self.game.right_click(pos)
        self.assertFalse(result)
    
    def test_cannot_click_flagged_cell(self):
        """Test that flagged cells cannot be clicked."""
        pos = Position(0, 0)
        
        # Flag the cell
        self.game.right_click(pos)
        
        # Try to click flagged cell
        revealed = self.game.left_click(pos)
        self.assertEqual(len(revealed), 0)  # No cells should be revealed
    
    def test_game_over_states(self):
        """Test game over detection."""
        self.assertFalse(self.game.is_game_over())
        self.assertFalse(self.game.is_won())
        self.assertFalse(self.game.is_lost())
        
        # Simulate loss
        self.game.game_state = GameState.LOST
        self.assertTrue(self.game.is_game_over())
        self.assertTrue(self.game.is_lost())
        self.assertFalse(self.game.is_won())
        
        # Simulate win
        self.game.game_state = GameState.WON
        self.assertTrue(self.game.is_game_over())
        self.assertFalse(self.game.is_lost())
        self.assertTrue(self.game.is_won())


class TestGameLogic(unittest.TestCase):
    """Integration tests for game logic."""
    
    def setUp(self):
        """Set up test game with controlled randomization."""
        self.config = GameConfig(3, 3, 1)  # Small grid with 1 mine
        
    @patch('random.sample')
    def test_win_condition(self, mock_sample):
        """Test win condition detection."""
        game = MinesweeperGame(self.config)
        
        # Place mine at position (2, 2)
        mock_sample.return_value = [Position(2, 2)]
        
        # Click all cells except the mine
        for row in range(3):
            for col in range(3):
                pos = Position(row, col)
                if pos != Position(2, 2):  # Don't click the mine
                    game.left_click(pos)
        
        # Game should be won
        self.assertTrue(game.is_won())
    
    @patch('random.sample')
    def test_lose_condition(self, mock_sample):
        """Test lose condition detection."""
        game = MinesweeperGame(self.config)
        
        # Place mine at position (1, 1)
        mock_sample.return_value = [Position(1, 1)]
        
        # First click somewhere safe
        game.left_click(Position(0, 0))
        
        # Then click the mine
        game.left_click(Position(1, 1))
        
        # Game should be lost
        self.assertTrue(game.is_lost())
    
    @patch('random.sample')
    def test_empty_cell_reveal(self, mock_sample):
        """Test that clicking empty cells reveals connected area."""
        game = MinesweeperGame(self.config)
        
        # Place mine at corner
        mock_sample.return_value = [Position(2, 2)]
        
        # Click center - should reveal multiple cells
        revealed = game.left_click(Position(1, 1))
        
        # Should reveal multiple connected cells
        self.assertGreater(len(revealed), 1)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_imports(self):
        """Test that all modules can be imported."""
        try:
            from constants import Difficulty, GAME_CONFIGS
            from models import Cell, Position, GameState
            from game_logic import MinesweeperGame
            from ui_components import ImageManager
            from utils import validate_game_config, GameTimer
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_game_config_validation(self):
        """Test game configuration validation."""
        from utils import validate_game_config
        
        # Valid configuration
        valid, msg = validate_game_config(9, 9, 10)
        self.assertTrue(valid)
        
        # Invalid configurations
        valid, msg = validate_game_config(0, 9, 10)
        self.assertFalse(valid)
        
        valid, msg = validate_game_config(9, 9, -1)
        self.assertFalse(valid)
        
        valid, msg = validate_game_config(3, 3, 9)
        self.assertFalse(valid)  # Too many mines


if __name__ == '__main__':
    # Set random seed for reproducible tests
    random.seed(42)
    
    # Run tests
    unittest.main(verbosity=2)
