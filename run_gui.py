"""
EarlyCare Gateway - GUI Launcher

Launch the graphical user interface for EarlyCare Gateway.

Usage:
    python run_gui.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import main

if __name__ == "__main__":
    main()
