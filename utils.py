"""
Utility functions and helpers for the Minesweeper game.
"""

import logging
from typing import List, Tuple
from pathlib import Path

from constants import BOMB_IMAGE_PATH, FLAG_IMAGE_PATH


def setup_logging(level: int = logging.INFO) -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('minesweeper.log')
        ]
    )


def create_assets_directory() -> None:
    """Create assets directory if it doesn't exist."""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)


def check_required_files() -> List[str]:
    """Check if all required files exist and return list of missing files."""
    missing_files = []
    
    required_files = [BOMB_IMAGE_PATH, FLAG_IMAGE_PATH]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    return missing_files


def create_placeholder_images() -> None:
    """Create placeholder images if they don't exist."""
    try:
        from PIL import Image
        
        # Create assets directory
        create_assets_directory()
        
        # Create bomb placeholder
        if not Path(BOMB_IMAGE_PATH).exists():
            bomb_img = Image.new('RGB', (35, 35), color='red')
            bomb_img.save(BOMB_IMAGE_PATH)
            print(f"Created placeholder bomb image at {BOMB_IMAGE_PATH}")
        
        # Create flag placeholder
        if not Path(FLAG_IMAGE_PATH).exists():
            flag_img = Image.new('RGB', (35, 35), color='yellow')
            flag_img.save(FLAG_IMAGE_PATH)
            print(f"Created placeholder flag image at {FLAG_IMAGE_PATH}")
            
    except ImportError:
        print("PIL not available, cannot create placeholder images")
    except Exception as e:
        print(f"Error creating placeholder images: {e}")


def validate_game_config(rows: int, cols: int, mines: int) -> Tuple[bool, str]:
    """Validate game configuration parameters."""
    if rows <= 0 or cols <= 0:
        return False, "Rows and columns must be positive"
    
    if mines < 0:
        return False, "Number of mines cannot be negative"
    
    total_cells = rows * cols
    if mines >= total_cells:
        return False, "Too many mines for the grid size"
    
    # Leave at least 9 cells for the first click (center + 8 neighbors)
    max_mines = max(0, total_cells - 9)
    if mines > max_mines:
        return False, f"Maximum {max_mines} mines allowed for {rows}x{cols} grid"
    
    return True, "Valid configuration"


def get_system_info() -> dict:
    """Get system information for debugging."""
    import platform
    import sys
    
    return {
        "platform": platform.system(),
        "python_version": sys.version,
        "platform_version": platform.version(),
        "architecture": platform.machine(),
    }


class GameTimer:
    """Simple game timer utility."""
    
    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0
        self.running = False
    
    def start(self) -> None:
        """Start the timer."""
        import time
        self.start_time = time.time()
        self.running = True
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time."""
        import time
        if self.running:
            self.end_time = time.time()
            self.running = False
        return self.get_elapsed_time()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        import time
        if self.running:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def get_formatted_time(self) -> str:
        """Get formatted elapsed time as MM:SS."""
        elapsed = self.get_elapsed_time()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"


def debug_grid(grid: List[List[any]], reveal_all: bool = False) -> str:
    """Create a string representation of the game grid for debugging."""
    if not grid or not grid[0]:
        return "Empty grid"
    
    result = []
    for row in grid:
        row_str = ""
        for cell in row:
            if hasattr(cell, 'value') and hasattr(cell, 'is_revealed') and hasattr(cell, 'is_flagged'):
                if reveal_all or cell.is_revealed:
                    if cell.is_mine:
                        row_str += " * "
                    elif cell.value == 0:
                        row_str += " . "
                    else:
                        row_str += f" {cell.value} "
                elif cell.is_flagged:
                    row_str += " F "
                else:
                    row_str += " ? "
            else:
                row_str += " ? "
        result.append(row_str)
    
    return "\n".join(result)
