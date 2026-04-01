#!/usr/bin/env python3
"""
OpenCode Command System - Main Dispatcher

This module provides the core command dispatching functionality for OpenCode.
It maps command names to their corresponding implementations and handles
command execution, argument parsing, and error handling.
"""

import sys
from collections.abc import Callable
from typing import Any


class CommandSystem:
    """Main command system dispatcher and manager."""

    def __init__(self):
        self.commands: dict[str, Callable] = {}
        self.command_descriptions: dict[str, str] = {}
        self.command_usage: dict[str, str] = {}

    def register_command(
        self, name: str, func: Callable, description: str, usage: str = ""
    ):
        """Register a new command with the system."""
        self.commands[name] = func
        self.command_descriptions[name] = description
        self.command_usage[name] = usage

    def get_command(self, name: str) -> Callable | None:
        """Get a registered command by name."""
        return self.commands.get(name)

    def list_commands(self) -> dict[str, str]:
        """List all available commands with descriptions."""
        return self.command_descriptions.copy()

    def execute_command(self, name: str, args: list | None = None) -> Any:
        if args is None:
            args = []

        command = self.get_command(name)
        if not command:
            print(f"Error: Command '{name}' not found.")
            self.print_help()
            return None

        try:
            parser = getattr(command, "parser", None)
            if parser:
                parsed_args = parser.parse_args(args)
                return command(parsed_args)
            else:
                return command(*args)

        except Exception as e:
            print(f"Error executing command '{name}': {e}")
            return None

    def print_help(self):
        """Print help information for all commands."""
        print("OpenCode Command System")
        print("=======================")
        print("Available commands:")
        print()

        commands = self.list_commands()
        max_len = max(len(cmd) for cmd in commands) if commands else 0

        for cmd, desc in sorted(commands.items()):
            padding = " " * (max_len - len(cmd) + 2)
            usage = self.command_usage.get(cmd, "")
            if usage:
                print(f"  {cmd}{padding}{desc}")
                print(f"    Usage: {usage}")
            else:
                print(f"  {cmd}{padding}{desc}")
            print()


system = CommandSystem()


def register_command(name: str, description: str, usage: str = ""):
    """Decorator to register a command."""

    def decorator(func):
        system.register_command(name, func, description, usage)
        return func

    return decorator


def main():
    """Main entry point for the command system."""
    if len(sys.argv) < 2:
        system.print_help()
        return 0

    command_name = sys.argv[1]
    args = sys.argv[2:]

    result = system.execute_command(command_name, args)
    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())
