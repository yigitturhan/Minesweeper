#!/usr/bin/env python3
"""
Main entry point for the Minesweeper game application.

This module handles application initialization, error handling,
and provides command-line interface options.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils import setup_logging, create_placeholder_images, check_required_files
from gui import MinesweeperGUI


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Minesweeper Game - A modern implementation of the classic game"
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Run unit tests instead of starting the game'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--create-assets',
        action='store_true',
        help='Create placeholder image assets and exit'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check dependencies and assets'
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if all dependencies are available."""
    missing_deps = []
    
    # Check PIL/Pillow
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_deps.append("Pillow (PIL)")
    
    # Check tkinter
    try:
        import tkinter as tk
    except ImportError:
        missing_deps.append("tkinter")
    
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True


def check_assets():
    """Check if assets are available."""
    missing_files = check_required_files()
    
    if missing_files:
        print("Missing asset files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nThe game will create placeholder images automatically.")
        print("For better visuals, add bomb.png and flag.png to the assets/ directory.")
    else:
        print("All asset files found.")
    
    return len(missing_files) == 0


def run_tests():
    """Run the test suite."""
    try:
        import unittest
        print("Running Minesweeper test suite...")
        print("=" * 50)
        
        # Import and run tests
        import tests
        
        # Create test loader and suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Return exit code based on test results
        return 0 if result.wasSuccessful() else 1
        
    except ImportError as e:
        print(f"Could not import test module: {e}")
        return 1


def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Minesweeper application")
    
    try:
        # Handle special commands
        if args.test:
            return run_tests()
        
        if args.create_assets:
            print("Creating placeholder assets...")
            create_placeholder_images()
            print("Placeholder assets created successfully.")
            return 0
        
        if args.check_deps:
            print("Checking dependencies...")
            deps_ok = check_dependencies()
            print("\nChecking assets...")
            assets_ok = check_assets()
            
            if deps_ok and assets_ok:
                print("\n✓ All dependencies and assets are available.")
                return 0
            else:
                print("\n✗ Some dependencies or assets are missing.")
                return 1
        
        # Check dependencies before starting game
        if not check_dependencies():
            return 1
        
        # Create placeholder images if needed
        missing_files = check_required_files()
        if missing_files:
            logger.info("Creating placeholder images for missing assets")
            create_placeholder_images()
        
        # Start the game
        logger.info("Initializing game GUI")
        app = MinesweeperGUI()
        
        logger.info("Starting main game loop")
        app.run()
        
        logger.info("Game application terminated normally")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        print("\nGame interrupted by user.")
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error: Missing required module - {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
        print("Please check the log file for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
