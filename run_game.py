#!/usr/bin/env python3
"""
FaceFury Launcher Script
Simple entry point to run the game from the project root.
"""

import sys
import os

# Add facefury to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'facefury'))

# Import and run main
from facefury.main import main

if __name__ == "__main__":
    main()
