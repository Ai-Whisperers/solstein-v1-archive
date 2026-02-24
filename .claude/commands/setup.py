#!/usr/bin/env python3
"""
OpenCode Command System - Setup and Installation

This script sets up the command system and makes it executable.
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_command_system():
    """Setup the command system."""
    print("Setting up OpenCode Command System...")

    commands_dir = Path(".claude/commands")
    commands_dir.mkdir(parents=True, exist_ok=True)

    for cmd_file in commands_dir.glob("*.py"):
        cmd_file.chmod(0o755)
        print(f"Made {cmd_file.name} executable")

    print("Command system setup complete!")
    print()
    print("To use the command system, run:")
    print("    python -m .claude.commands [command] [args]")
    print()
    print("Available commands:")
    print("    hello    - Say hello to someone")
    print("    add      - Add two numbers")
    print("    version  - Show OpenCode version")
    print("    list     - List available commands")
    print("    help     - Show help for a command")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        setup_command_system()
    else:
        print("OpenCode Command System")
        print("=======================")
        print()
        print("Usage:")
        print("  python setup.py --install    # Setup the command system")
        print("  python -m .claude.commands   # Run the command system")
        print()
        print("Run 'python setup.py --install' to setup the command system.")


if __name__ == "__main__":
    main()
