"""
UI components for the Minesweeper game.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Dict, Any
from PIL import Image, ImageTk
import os

from constants import *
from models import Cell, Position


class ImageManager:
    """Manages game images with error handling and caching."""
    
    def __init__(self):
        self._images: Dict[str, ImageTk.PhotoImage] = {}
        # Don't load images immediately - load them when needed
        self._images_loaded = False
    
    def _ensure_images_loaded(self) -> None:
        """Load images if not already loaded."""
        if not self._images_loaded:
            try:
                self._load_images()
                self._images_loaded = True
            except Exception as e:
                print(f"Warning: Could not load images: {e}")
                # Create text-based fallbacks
                self._images = {}
    
    def _load_images(self) -> None:
        """Load and cache all game images."""
        self._load_image("bomb", BOMB_IMAGE_PATH)
        self._load_image("flag", FLAG_IMAGE_PATH)
    
    def _load_image(self, name: str, path: str) -> None:
        """Load a single image with error handling."""
        try:
            if os.path.exists(path):
                img = Image.open(path)
                resized_img = img.resize(IMAGE_SIZE)
                self._images[name] = ImageTk.PhotoImage(resized_img)
            else:
                # Skip creating placeholder here - will be handled in get_image
                pass
        except Exception as e:
            print(f"Warning: Could not load {path}: {e}")
    
    def get_image(self, name: str) -> Optional[ImageTk.PhotoImage]:
        """Get image by name, loading if necessary."""
        self._ensure_images_loaded()
        
        # If image exists, return it
        if name in self._images:
            return self._images[name]
        
        # Try to create a simple placeholder if needed
        try:
            # Create a simple colored rectangle as placeholder
            color = 'red' if name == 'bomb' else 'yellow'
            img = Image.new('RGB', IMAGE_SIZE, color=color)
            self._images[name] = ImageTk.PhotoImage(img)
            return self._images[name]
        except Exception:
            # If even placeholder fails, return None (will show text)
            return None


class CellWidget:
    """Widget representing a single minesweeper cell."""
    
    def __init__(self, parent: tk.Widget, pos: Position, image_manager: ImageManager,
                 left_click_callback: Callable[[Position], None],
                 right_click_callback: Callable[[Position], None]):
        self.pos = pos
        self.image_manager = image_manager
        self.left_click_callback = left_click_callback
        self.right_click_callback = right_click_callback
        
        self.label = tk.Label(
            parent,
            width=CELL_WIDTH,
            height=CELL_HEIGHT,
            relief=tk.RAISED,
            bg=BG_COLOR,
            font=FONT_NORMAL,
            borderwidth=2
        )
        
        self._bind_events()
    
    def _bind_events(self) -> None:
        """Bind mouse events to the cell."""
        self.label.bind(LEFT_CLICK, lambda e: self.left_click_callback(self.pos))
        self.label.bind(RIGHT_CLICK, lambda e: self.right_click_callback(self.pos))
    
    def update_display(self, cell: Cell, game_over: bool = False) -> None:
        """Update the visual representation of the cell."""
        if cell.is_flagged and not game_over:
            self._show_flag()
        elif cell.is_revealed:
            if cell.is_mine:
                self._show_mine(hit=game_over)
            elif cell.value == 0:
                self._show_empty()
            else:
                self._show_number(cell.value)
        else:
            self._show_hidden()
    
    def _show_flag(self) -> None:
        """Display flag image."""
        flag_image = self.image_manager.get_image("flag")
        if flag_image:
            self.label.configure(image=flag_image, text="", bg=BG_COLOR)
            self.label.image = flag_image  # Keep reference
        else:
            self.label.configure(text="🚩", bg="yellow", image="")
    
    def _show_mine(self, hit: bool = False) -> None:
        """Display mine image."""
        bomb_image = self.image_manager.get_image("bomb")
        bg_color = MINE_BG_COLOR if hit else OPENED_BG_COLOR
        
        if bomb_image:
            self.label.configure(image=bomb_image, text="", bg=bg_color)
            self.label.image = bomb_image  # Keep reference
        else:
            self.label.configure(text="💣", bg=bg_color, fg="black", image="")
    
    def _show_empty(self) -> None:
        """Display empty revealed cell."""
        self.label.configure(
            text="",
            bg=OPENED_BG_COLOR,
            relief=tk.SUNKEN,
            image=""
        )
    
    def _show_number(self, number: int) -> None:
        """Display numbered cell."""
        color = COLOR_MAPPING.get(number, 'black')
        self.label.configure(
            text=str(number),
            bg=OPENED_BG_COLOR,
            fg=color,
            relief=tk.SUNKEN,
            image=""
        )
    
    def _show_hidden(self) -> None:
        """Display hidden cell."""
        self.label.configure(
            text="",
            bg=BG_COLOR,
            relief=tk.RAISED,
            image=""
        )
    
    def grid(self, row: int, column: int) -> None:
        """Place the cell in the grid."""
        self.label.grid(row=row, column=column, padx=1, pady=1)


class StatusBar:
    """Status bar showing game information."""
    
    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent, bg=OPENED_BG_COLOR, relief=tk.SUNKEN, bd=1)
        
        self.mines_label = tk.Label(
            self.frame,
            text="Mines: 0",
            bg=OPENED_BG_COLOR,
            font=FONT_NORMAL
        )
        self.mines_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.status_label = tk.Label(
            self.frame,
            text="Ready",
            bg=OPENED_BG_COLOR,
            font=FONT_NORMAL
        )
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def update_mines(self, remaining_mines: int) -> None:
        """Update the mines counter."""
        self.mines_label.configure(text=f"Mines: {remaining_mines}")
    
    def update_status(self, status: str) -> None:
        """Update the status message."""
        self.status_label.configure(text=status)
    
    def pack(self, **kwargs) -> None:
        """Pack the status bar."""
        self.frame.pack(**kwargs)


class GameOverDialog:
    """Dialog shown when game ends."""
    
    @staticmethod
    def show_game_over(parent: tk.Widget, won: bool, callback: Callable[[], None]) -> None:
        """Show game over dialog."""
        title = "Congratulations!" if won else "Game Over"
        message = "You won! 🎉" if won else "Better luck next time! 💣"
        
        result = messagebox.askyesno(
            title,
            f"{message}\n\nWould you like to play again?",
            parent=parent
        )
        
        if result:
            callback()


class DifficultyDialog:
    """Dialog for selecting game difficulty."""
    
    def __init__(self, parent: tk.Widget, callback: Callable[[Difficulty], None]):
        self.callback = callback
        self.result: Optional[Difficulty] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Difficulty")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("300x200+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self._create_widgets()
        
        # Wait for dialog to close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.dialog.wait_window()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        tk.Label(
            self.dialog,
            text="Choose Difficulty Level",
            font=FONT_LARGE
        ).pack(pady=20)
        
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        for difficulty in Difficulty:
            config = GAME_CONFIGS[difficulty]
            text = f"{difficulty.value.title()}\n({config.rows}x{config.cols}, {config.mines} mines)"
            
            btn = tk.Button(
                button_frame,
                text=text,
                width=15,
                height=3,
                command=lambda d=difficulty: self._on_select(d)
            )
            btn.pack(pady=5)
    
    def _on_select(self, difficulty: Difficulty) -> None:
        """Handle difficulty selection."""
        self.result = difficulty
        self.dialog.destroy()
        if self.callback:
            self.callback(difficulty)
    
    def _on_cancel(self) -> None:
        """Handle dialog cancellation."""
        self.result = None
        self.dialog.destroy()
