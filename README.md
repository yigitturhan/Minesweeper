# Minesweeper Game

A modern, well-structured implementation of the classic Minesweeper game built with Python and Tkinter.

## Features

- **Three Difficulty Levels**: Beginner (9x9, 10 mines), Intermediate (16x16, 40 mines), Expert (30x16, 99 mines)
- **Modern GUI**: Clean, intuitive interface with visual feedback
- **Smart First Click**: First click is always safe and won't hit a mine
- **Chord Clicking**: Middle-click or left+right click to reveal adjacent cells when enough flags are placed
- **Visual Assets**: Custom bomb and flag images with fallback to text
- **Game Statistics**: Mine counter and game status tracking
- **Error Handling**: Robust error handling and graceful degradation

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create assets directory** (optional):
   ```bash
   mkdir assets
   ```
   Add `bomb.png` and `flag.png` images to the assets folder, or the game will create simple placeholder images.

## Usage

### Running the Game

```bash
python gui.py
```

### Game Controls

- **Left Click**: Reveal cell
- **Right Click**: Toggle flag
- **Chord Click**: On revealed numbered cells, if the correct number of adjacent cells are flagged, reveal remaining adjacent cells

### Game Rules

1. The objective is to reveal all cells that don't contain mines
2. Numbers indicate how many mines are adjacent to that cell
3. Right-click to flag suspected mines
4. The game is won when all non-mine cells are revealed
5. The game is lost if you click on a mine

## Project Structure

```
minesweeper/
├── constants.py      # Game constants and configuration
├── models.py         # Data models (Cell, Position, GameStats)
├── game_logic.py     # Core game logic and algorithms
├── ui_components.py  # GUI components and widgets
├── gui.py           # Main application and GUI controller
├── utils.py         # Utility functions and helpers
├── tests.py         # Unit tests
├── requirements.txt # Dependencies
├── README.md        # This file
└── assets/          # Image assets (optional)
    ├── bomb.png
    └── flag.png
```

## Architecture

The project follows modern software development principles:

### **Separation of Concerns**
- **Models** (`models.py`): Data structures and game state
- **Logic** (`game_logic.py`): Game rules and algorithms
- **UI** (`ui_components.py`, `gui.py`): User interface components
- **Constants** (`constants.py`): Configuration and constants

### **Object-Oriented Design**
- Clear class hierarchies and responsibilities
- Encapsulation of game state and behavior
- Use of dataclasses and enums for type safety

### **Error Handling**
- Custom exceptions for game-specific errors
- Graceful degradation when assets are missing
- Input validation and bounds checking

### **Testing**
- Comprehensive unit tests covering core functionality
- Mock objects for testing randomized behavior
- Integration tests for game scenarios

## Key Classes

### `MinesweeperGame`
Core game logic including:
- Mine placement with safe first click
- Cell revelation algorithms
- Win/lose condition checking
- Flag management

### `Cell`
Represents individual cells with:
- Value (mine or adjacent mine count)
- State (hidden, revealed, flagged)
- Type-safe state transitions

### `Position`
Coordinate system with:
- Neighbor calculation
- Bounds checking
- Hash support for set operations

### `CellWidget`
GUI representation of cells with:
- Visual state management
- Event handling
- Image display with fallbacks

## Advanced Features

### **Flood Fill Algorithm**
Efficient revelation of connected empty areas using BFS (Breadth-First Search).

### **Smart Mine Placement**
Mines are placed after the first click to ensure the first click is always safe and reveals a reasonable area.

### **Chord Clicking**
Advanced gameplay feature allowing quick revelation of cells when the correct number of adjacent mines are flagged.

### **Visual Feedback**
- Different colors for different numbers
- Visual distinction between game states
- Smooth UI updates and transitions

## Testing

Run the test suite:

```bash
python tests.py
```

The test suite includes:
- Unit tests for all core classes
- Integration tests for game scenarios
- Mock testing for randomized behavior
- Edge case validation

## Development

### Code Style
- Follows PEP 8 style guidelines
- Type hints throughout
- Comprehensive docstrings
- Clear variable and function names

### Adding Features

The modular architecture makes it easy to extend:

1. **New Difficulty Levels**: Add to `constants.py`
2. **Custom Themes**: Extend `ui_components.py`
3. **Game Modes**: Modify `game_logic.py`
4. **Statistics**: Extend `models.py`

### Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

## Troubleshooting

### Common Issues

**Images not displaying**: 
- Check if `assets/` directory exists
- Verify `bomb.png` and `flag.png` are present
- The game will create placeholder images if assets are missing

**Performance issues with large grids**:
- The Expert mode (30x16) is the maximum recommended size
- Consider optimizing the reveal algorithm for larger grids

**Import errors**:
- Ensure all Python files are in the same directory
- Check that Python 3.7+ is installed
- Install required dependencies with `pip install -r requirements.txt`

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Classic Minesweeper game design by Microsoft
- Built with Python's Tkinter for cross-platform compatibility
- Uses Pillow (PIL) for image handling
