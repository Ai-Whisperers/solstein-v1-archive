#!/usr/bin/env python3
"""
Example commands for the OpenCode command system.
These demonstrate different types of commands and patterns.
"""

from . import register_command


@register_command("hello", "Say hello to someone", "[name]")
def hello(args):
    """Say hello to someone."""
    name = args.name if hasattr(args, "name") else "World"
    print(f"Hello, {name}!")
    return 0


@register_command("add", "Add two numbers", "a b")
def add(args):
    """Add two numbers."""
    if not hasattr(args, "a") or not hasattr(args, "b"):
        print("Error: Please provide two numbers to add.")
        return 1

    try:
        result = float(args.a) + float(args.b)
        print(f"Result: {result}")
        return 0
    except ValueError:
        print("Error: Please provide valid numbers.")
        return 1


@register_command("version", "Show OpenCode version information", "")
def version():
    """Show OpenCode version information."""
    print("OpenCode Command System v1.0.0")
    print("Copyright © 2026 OpenCode")
    return 0


@register_command("list", "List available commands", "")
def list_commands():
    """List all available commands."""
    from . import system

    commands = system.list_commands()

    print("Available commands:")
    print()
    for cmd, desc in sorted(commands.items()):
        print(f"  {cmd}: {desc}")
    return 0


@register_command("help", "Show help for a specific command", "[command]")
def help_command(args):
    """Show help for a specific command."""
    if not hasattr(args, "command"):
        from . import system

        system.print_help()
        return 0

    command_name = args.command
    from . import system

    command = system.get_command(command_name)

    if not command:
        print(f"Error: Command '{command_name}' not found.")
        return 1

    # Get the command's argument parser if it has one
    parser = getattr(command, "parser", None)
    if parser:
        parser.print_help()
    else:
        print(f"Command: {command_name}")
        print(
            f"Description: {system.command_descriptions.get(command_name, 'No description')}"
        )
    return 0
