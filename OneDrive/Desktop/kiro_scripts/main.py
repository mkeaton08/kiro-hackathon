#!/usr/bin/env python3
"""
Mini CTF Game - Main Entry Point
A simple CLI-based Capture The Flag game for learning cybersecurity concepts.
"""

import sys
import os
from database import init_database, get_db_connection
from utils import print_banner, print_error, print_success

def main():
    """Main entry point for the CTF game."""
    print_banner("Welcome to Mini CTF Game!")
    
    # Initialize database on first run
    try:
        init_database()
        print_success("Database initialized successfully!")
    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # TODO: Add main menu and CLI argument parsing
    print("CTF Game is ready to run!")
    print("More functionality coming soon...")

if __name__ == "__main__":
    main()