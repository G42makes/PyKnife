#!/usr/bin/env python3
"""
mkdir command implementation.

The mkdir command creates directories.
"""

import sys
import os
import argparse
import stat


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="mkdir",
        description="Create the DIRECTORY(ies), if they do not already exist.",
        usage=argparse.SUPPRESS
    )
    
    # Directory arguments
    parser.add_argument(
        "directories", 
        nargs="+", 
        help="directory names to create"
    )
    
    # Create parent directories if needed
    parser.add_argument(
        "-p", "--parents", 
        action="store_true", 
        help="make parent directories as needed"
    )
    
    # Set permissions
    parser.add_argument(
        "-m", "--mode", 
        type=str,
        default="0777",
        help="set file mode (as in chmod), not a=rwx - umask"
    )
    
    # Verbose option
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="print a message for each created directory"
    )
    
    return parser.parse_args(args)


def parse_mode(mode_str):
    """
    Parse the mode string and return the corresponding integer mode.
    
    Args:
        mode_str: String representation of the mode
        
    Returns:
        int: Parsed mode as an integer
    """
    if mode_str.startswith('0'):
        # Parse as octal
        try:
            return int(mode_str, 8)
        except ValueError:
            raise ValueError(f"invalid mode: '{mode_str}'")
    else:
        # Assume decimal
        try:
            return int(mode_str)
        except ValueError:
            raise ValueError(f"invalid mode: '{mode_str}'")


def make_directory(directory, mode, parents=False, verbose=False):
    """
    Create a directory with the specified mode.
    
    Args:
        directory: Path to the directory to create
        mode: Permission mode to set
        parents: Whether to create parent directories as needed
        verbose: Whether to print messages about created directories
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if parents:
            # Check if the directory already exists before creating it
            dir_existed = os.path.exists(directory)
            
            # Create parent directories if they don't exist
            os.makedirs(directory, mode=mode, exist_ok=True)
            
            # Print message only if the directory was actually created
            if verbose and not dir_existed:
                print(f"mkdir: created directory '{directory}'")
            
            return True
        else:
            # Don't create parent directories
            if os.path.exists(directory):
                # Directory exists, this is an error for regular mkdir (without -p)
                print(f"mkdir: cannot create directory '{directory}': File exists", file=sys.stderr)
                return False
            
            try:
                os.mkdir(directory, mode=mode)
                if verbose:
                    print(f"mkdir: created directory '{directory}'")
            except FileNotFoundError:
                # Parent directory doesn't exist
                print(f"mkdir: cannot create directory '{directory}': No such file or directory", file=sys.stderr)
                return False
        
        return True
    except PermissionError as e:
        print(f"mkdir: cannot create directory '{directory}': Permission denied", file=sys.stderr)
        return False
    except OSError as e:
        print(f"mkdir: cannot create directory '{directory}': {e.strerror}", file=sys.stderr)
        return False


def main(args):
    """Main function for the mkdir command."""
    try:
        options = parse_args(args)
        
        # Parse the mode
        try:
            mode = parse_mode(options.mode)
        except ValueError as e:
            print(f"mkdir: {str(e)}", file=sys.stderr)
            return 1
        
        # Apply the umask
        umask = os.umask(0)
        os.umask(umask)  # Reset the umask
        effective_mode = mode & ~umask
        
        # Process each directory
        exit_code = 0
        for directory in options.directories:
            result = make_directory(
                directory,
                effective_mode,
                parents=options.parents,
                verbose=options.verbose
            )
            if not result:
                exit_code = 1
        
        return exit_code
        
    except Exception as e:
        print(f"mkdir: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 