#!/usr/bin/env python3
"""
PyKnife - Python implementation of common Linux CLI tools.

This CLI can be used in two ways:
1. By specifying the command as the first argument: `python cli.py echo "hello"`
2. By creating symlinks to this file with the command name and running them directly:
   - Create a symlink: `ln -s cli.py pwd` or `ln -s cli.py pwd.py`
   - Then run: `./pwd` or `python pwd.py`
"""

import sys
import argparse
import os
from importlib import import_module


def get_command_from_script_name(script_path):
    """
    Extract the command name from the script name.
    This allows the CLI to be invoked via symlinks.
    
    Examples:
    - 'cli.py' -> None (use command-line argument)
    - 'pwd' -> 'pwd'
    - 'pwd.py' -> 'pwd'
    - '/path/to/echo' -> 'echo'
    - '/path/to/echo.py' -> 'echo'
    """
    # Get just the filename without the path
    script_name = os.path.basename(script_path)
    
    # If it's the main CLI script, return None
    if script_name in ['cli.py', 'cli']:
        return None
    
    # Remove '.py' extension if present
    if script_name.endswith('.py'):
        script_name = script_name[:-3]
    
    return script_name


def main():
    """Main entry point for the CLI."""
    # Determine how the script was invoked
    script_path = sys.argv[0]
    command_from_name = get_command_from_script_name(script_path)
    
    if command_from_name:
        # Invoked via symlink (e.g., ./pwd or python pwd.py)
        command = command_from_name
        command_args = sys.argv[1:]  # All args are for the command
    elif len(sys.argv) < 2:
        # Invoked as cli.py but without a command
        print("Error: No command specified", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} COMMAND [ARGS]", file=sys.stderr)
        sys.exit(1)
    else:
        # Invoked as cli.py with a command
        command = sys.argv[1]
        command_args = sys.argv[2:]  # Skip the command name
    
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
