#!/usr/bin/env python3
"""
PyKnife - Python implementation of common Linux CLI tools.
"""

import sys
import argparse
from importlib import import_module


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print("Error: No command specified", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} COMMAND [ARGS]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    command_args = sys.argv[2:]

    try:
        # Import the command module
        command_module = import_module(f"commands.{command}", package="src")
        
        # Call the main function of the command
        return command_module.main(command_args)
    except ModuleNotFoundError:
        print(f"Error: Command '{command}' not found", file=sys.stderr)
        sys.exit(1)
    except AttributeError:
        print(f"Error: Command '{command}' is not properly implemented", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
