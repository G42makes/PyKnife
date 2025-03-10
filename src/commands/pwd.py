#!/usr/bin/env python3
"""
pwd command implementation.

The pwd command prints the name of the current/working directory.
"""

import os
import sys
import argparse


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="pwd",
        description="Print the current working directory",
        # Don't print usage when there's an error
        usage=argparse.SUPPRESS
    )
    
    # -P option: avoid all symlinks
    parser.add_argument(
        "-P", 
        action="store_true", 
        help="avoid all symlinks (use physical directory structure)"
    )
    
    # -L option: follow symlinks (default)
    parser.add_argument(
        "-L", 
        action="store_true", 
        help="follow symlinks (default)"
    )
    
    return parser.parse_args(args)


def main(args):
    """Main function for the pwd command."""
    parsed_args = parse_args(args)
    
    # Determine whether to avoid symlinks
    # -P takes precedence over -L if both are specified
    avoid_symlinks = parsed_args.P
    
    if avoid_symlinks:
        # Get the physical path (no symlinks)
        try:
            current_dir = os.path.realpath(os.getcwd())
        except OSError as e:
            print(f"pwd: error retrieving current directory: {e}", file=sys.stderr)
            return 1
    else:
        # Get the logical path (may contain symlinks)
        try:
            current_dir = os.getcwd()
        except OSError as e:
            print(f"pwd: error retrieving current directory: {e}", file=sys.stderr)
            return 1
    
    # Print the current directory
    print(current_dir)
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 