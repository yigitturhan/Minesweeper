"""
Main GUI application for Minesweeper.
"""

import tkinter as tk
from typing import List, Optional, Dict
import sys

from constants import *
from models import Position
from game_logic import MinesweeperGame
from ui_components import (
    CellWidget, StatusBar, GameOverDialog, DifficultyDialog, ImageManager
)


class MinesweeperGUI:
    """Main GUI application for Minesweeper."""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.game: Optional[MinesweeperGame] = None
        self.cell_widgets: List[List[CellWidget]] = []
        self.status_bar: Optional[StatusBar] = None
        self.image_manager: Optional[ImageManager] = None  # Changed: Don't initialize yet
        
        self._setup_root()
        self._initialize_image_manager()  # New: Initialize after root window
        self._show_difficulty_dialog()
    
    def _setup_root(self) -> None:
        """Setup the main window."""
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.resizable(False, False)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _initialize_image_manager(self) -> None:
        """Initialize image manager after root window is created."""
        if self.root:
            self.image_manager = ImageManager()
    
    def _show_difficulty_dialog(self) -> None:
        """Show difficulty selection dialog."""
        if not self.root:
            return
            
        DifficultyDialog(self.root, self._start_new_game)
    
    def _start_new_game(self, difficulty: Difficulty) -> None:
        """Start a new game with selected difficulty."""
        if not self.root:
            return
        
        # Clear existing game
        self._clear_game_area()
        
        # Create new game
        config = GAME_CONFIGS[difficulty]
        self.game = MinesweeperGame(config)
        
        # Setup UI
        self._setup_status_bar()
        self._setup_game_grid()
        self._update_display()
        
        # Update window size
        self.root.update_idletasks()
        self.root.geometry("")  # Auto-size
    
    def _clear_game_area(self) -> None:
        """Clear the game area."""
        if self.root:
            for widget in self.root.winfo_children():
                widget.destroy()
        self.cell_widgets = []
        self.status_bar = None
    
    def _setup_status_bar(self) -> None:
        """Setup the status bar."""
        if not self.root:
            return
            
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def _setup_game_grid(self) -> None:
        """Setup the game grid."""
        if not self.root or not self.game or not self.image_manager:
            return
        
        # Create game frame
        game_frame = tk.Frame(self.root, bg=OPENED_BG_COLOR)
        game_frame.pack(padx=10, pady=10)
        
        # Create cell widgets
        self.cell_widgets = []
        for row in range(self.game.config.rows):
            widget_row = []
            for col in range(self.game.config.cols):
                pos = Position(row, col)
                cell_widget = CellWidget(
                    game_frame,
                    pos,
                    self.image_manager,
                    self._on_left_click,
                    self._on_right_click
                )
                cell_widget.grid(row, col)
                widget_row.append(cell_widget)
            self.cell_widgets.append(widget_row)
    
    def _on_left_click(self, pos: Position) -> None:
        """Handle left click on a cell."""
        if not self.game or self.game.is_game_over():
            return
        
        try:
            revealed_positions = self.game.left_click(pos)
            self._update_display(revealed_positions)
            
            if self.game.is_game_over():
                self._handle_game_over()
                
        except Exception as e:
            print(f"Error handling left click: {e}")
    
    def _on_right_click(self, pos: Position) -> None:
        """Handle right click on a cell."""
        if not self.game or self.game.is_game_over():
            return
        
        try:
            self.game.right_click(pos)
            self._update_display({pos})
            
        except Exception as e:
            print(f"Error handling right click: {e}")
    
    def _update_display(self, updated_positions: Optional[set] = None) -> None:
        """Update the display for specified positions or all positions."""
        if not self.game or not self.status_bar:
            return
        
        # Update status bar
        self.status_bar.update_mines(self.game.stats.remaining_mines)
        
        if self.game.is_won():
            self.status_bar.update_status("You Won! 🎉")
        elif self.game.is_lost():
            self.status_bar.update_status("Game Over 💣")
        else:
            self.status_bar.update_status("Playing...")
        
        # Update cells
        if updated_positions is None:
            # Update all cells
            for row in range(self.game.config.rows):
                for col in range(self.game.config.cols):
                    pos = Position(row, col)
                    cell = self.game.get_cell(pos)
                    self.cell_widgets[row][col].update_display(cell, self.game.is_lost())
        else:
            # Update only specified cells
            for pos in updated_positions:
                if (0 <= pos.row < len(self.cell_widgets) and 
                    0 <= pos.col < len(self.cell_widgets[0])):
                    cell = self.game.get_cell(pos)
                    self.cell_widgets[pos.row][pos.col].update_display(cell, self.game.is_lost())
    
    def _handle_game_over(self) -> None:
        """Handle game over state."""
        if not self.game:
            return
        
        if self.game.is_lost():
            # Reveal all mines
            mine_positions = self.game.reveal_all_mines()
            self._update_display(set(mine_positions))
        
        # Show game over dialog after a short delay
        if self.root:
            self.root.after(500, lambda: GameOverDialog.show_game_over(
                self.root,
                self.game.is_won(),
                self._show_difficulty_dialog
            ))
    
    def _on_close(self) -> None:
        """Handle window close event."""
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def run(self) -> None:
        """Start the GUI application."""
        if self.root:
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                self._on_close()


def main():
    """Main entry point."""
    try:
        app = MinesweeperGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
