"""
Utility functions for Mini CTF Game
Provides console formatting, colors, and helper functions.
"""

import os
import sys
from datetime import datetime

# ANSI color codes for console output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_banner(text):
    """Print a colorful banner message."""
    border = "=" * (len(text) + 4)
    print(f"\n{Colors.CYAN}{Colors.BOLD}{border}")
    print(f"  {text}")
    print(f"{border}{Colors.END}\n")

def print_success(text):
    """Print a success message in green."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print an error message in red."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Print an info message in blue."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_header(text):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}{text}{Colors.END}")

def print_table_header(headers):
    """Print a formatted table header."""
    header_line = " | ".join(f"{header:^15}" for header in headers)
    separator = "-" * len(header_line)
    
    print(f"\n{Colors.BOLD}{header_line}{Colors.END}")
    print(separator)

def print_table_row(values):
    """Print a formatted table row."""
    row_line = " | ".join(f"{str(value):^15}" for value in values)
    print(row_line)

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input(prompt, input_type=str, required=True):
    """Get user input with validation."""
    while True:
        try:
            user_input = input(f"{Colors.CYAN}{prompt}{Colors.END}")
            
            if not user_input.strip() and required:
                print_error("This field is required. Please try again.")
                continue
            
            if input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return user_input.strip()
                
        except ValueError:
            print_error(f"Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Operation cancelled.{Colors.END}")
            return None

def format_datetime(dt_string):
    """Format datetime string for display."""
    if not dt_string:
        return "Never"
    
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_string

def truncate_text(text, max_length=50):
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def confirm_action(message):
    """Ask user to confirm an action."""
    response = get_user_input(f"{message} (y/N): ", required=False)
    return response.lower() in ['y', 'yes']

def pause():
    """Pause execution until user presses Enter."""
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

def print_menu(title, options):
    """Print a formatted menu with options."""
    print_header(title)
    
    for i, option in enumerate(options, 1):
        print(f"{Colors.CYAN}{i}.{Colors.END} {option}")
    
    print()

def get_menu_choice(max_options):
    """Get a valid menu choice from user."""
    while True:
        try:
            choice = int(get_user_input("Enter your choice: "))
            if 1 <= choice <= max_options:
                return choice
            else:
                print_error(f"Please enter a number between 1 and {max_options}.")
        except ValueError:
            print_error("Please enter a valid number.")
        except TypeError:  # get_user_input returned None (Ctrl+C)
            return None