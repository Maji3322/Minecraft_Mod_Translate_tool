"""
Entry point for the Minecraft MOD Translator Tool.
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the src package
from src.main import main

if __name__ == "__main__":
    main()
