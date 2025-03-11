#!/usr/bin/env python3
"""
Setup symlinks for PyKnife commands.

This script creates symlinks in the specified directory for all available
PyKnife commands, pointing to the main CLI script. This allows commands
to be invoked directly by name, similar to how BusyBox works.
"""

import os
import sys
import argparse
import importlib
import shutil
from pathlib import Path


def get_available_commands():
    """Get a list of all available PyKnife commands."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.commands import __all__ as commands
        return commands
    except (ImportError, AttributeError):
        print("Error: Could not import command list from src.commands", file=sys.stderr)
        return []


def setup_symlinks(target_dir, use_py_extension=False, force=False):
    """
    Create symlinks for all PyKnife commands.
    
    Args:
        target_dir (str): Directory where symlinks will be created
        use_py_extension (bool): Whether to add .py extension to symlinks
        force (bool): Whether to overwrite existing files
    """
    commands = get_available_commands()
    if not commands:
        print("No commands found to create symlinks for.", file=sys.stderr)
        return 1
    
    # Get the absolute path to the CLI script
    cli_script = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'src', 'cli.py'
    ))
    
    # Ensure the target directory exists
    target_dir = os.path.abspath(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    # Create symlinks for all commands
    created = 0
    skipped = 0
    for command in commands:
        # Determine the symlink name
        symlink_name = f"{command}.py" if use_py_extension else command
        symlink_path = os.path.join(target_dir, symlink_name)
        
        # Check if the symlink already exists
        if os.path.exists(symlink_path):
            if force:
                try:
                    os.remove(symlink_path)
                except OSError as e:
                    print(f"Warning: Could not remove existing file '{symlink_path}': {e}")
                    skipped += 1
                    continue
            else:
                print(f"Skipping: '{symlink_path}' already exists (use --force to overwrite)")
                skipped += 1
                continue
        
        # Create the symlink
        try:
            # Use relative path for the target if possible
            try:
                # Get relative path from symlink to cli.py
                target = os.path.relpath(cli_script, target_dir)
            except ValueError:
                # If on different drives (Windows), use absolute path
                target = cli_script
            
            # Create the symlink
            if os.name == 'nt':  # Windows
                # Windows requires admin privileges for symlinks, so copy instead
                shutil.copy2(cli_script, symlink_path)
                print(f"Created copy: {symlink_path} -> {target}")
            else:
                # Unix systems can use symlinks
                os.symlink(target, symlink_path)
                print(f"Created symlink: {symlink_path} -> {target}")
            created += 1
        except OSError as e:
            print(f"Error creating symlink '{symlink_path}': {e}")
            skipped += 1
    
    print(f"\nSummary: Created {created} symlinks, skipped {skipped}")
    
    if created > 0:
        print("\nYou can now run commands directly:")
        example_cmd = next(iter(commands))
        example_path = os.path.join(target_dir, example_cmd)
        if os.name == 'nt':  # Windows
            example_path += ".py" if use_py_extension else ""
            print(f"  python {example_path} [ARGS]")
        else:
            print(f"  {example_path} [ARGS]")
    
    return 0


def main():
    """Parse command line arguments and setup symlinks."""
    parser = argparse.ArgumentParser(description="Create symlinks for PyKnife commands")
    parser.add_argument(
        "target_dir", 
        help="Directory where symlinks will be created"
    )
    parser.add_argument(
        "--py", action="store_true",
        help="Add .py extension to symlinks"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing files"
    )
    
    args = parser.parse_args()
    
    return setup_symlinks(args.target_dir, args.py, args.force)


if __name__ == "__main__":
    sys.exit(main()) 