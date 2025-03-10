#!/usr/bin/env python3
"""
PyKnife - Python implementation of common Linux CLI tools.
"""

import sys
import argparse
import os
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
        # Add the parent directory to sys.path so imports work correctly
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Import the command module
        command_module = import_module(f"src.commands.{command}")
        
        # Call the main function of the command
        return command_module.main(command_args)
    except ModuleNotFoundError as e:
        print(f"Error: Command '{command}' not found ({str(e)})", file=sys.stderr)
        sys.exit(1)
    except AttributeError as e:
        print(f"Error: Command '{command}' is not properly implemented ({str(e)})", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing command '{command}': {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
