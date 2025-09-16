#!/usr/bin/env python3
"""
ChronoCLI - Personal Time Tracker

A command-line tool for tracking and analyzing work hours with support for
German date formats and flexible data input methods.

Author: ChronoCLI Team
Version: 1.0.0 (Phase 1)
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import ChronoCLIUI


def main():
    """Main entry point for the ChronoCLI application."""
    print("⏰  Welcome to ChronoCLI - Personal Time Tracker")
    print("=" * 50)
    print("Phase 1: Core Functionality & MVP")
    print("=" * 50)
    
    # Create and run the UI
    app = ChronoCLIUI()
    app.run()


if __name__ == "__main__":
    main()