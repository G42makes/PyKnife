#!/usr/bin/env python3
"""
head command implementation.

The head command outputs the first part of files.
"""

import sys
import os
import argparse


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="head",
        description="Output the first part of files",
        usage=argparse.SUPPRESS
    )
    
    # File arguments
    parser.add_argument(
        "files", 
        nargs="*", 
        help="the files to read"
    )
    
    # Number of lines/bytes to output
    parser.add_argument(
        "-n", "--lines", 
        type=int, 
        default=10, 
        help="print the first NUM lines instead of the first 10"
    )
    
    parser.add_argument(
        "-c", "--bytes", 
        type=int, 
        help="print the first NUM bytes of each file"
    )
    
    parser.add_argument(
        "-q", "--quiet", "--silent", 
        action="store_true", 
        help="never print headers giving file names"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="always print headers giving file names"
    )
    
    return parser.parse_args(args)


def head_file(file_path, options, file_number, total_files):
    """
    Process a single file according to the head options.
    
    Args:
        file_path: Path to the file to process, or "-" for stdin.
        options: Command options.
        file_number: Current file number (for header output).
        total_files: Total number of files (for header output).
        
    Returns:
        int: 0 on success, 1 on error.
    """
    # Determine whether to print headers
    print_header = True
    if options.quiet:
        print_header = False
    elif not options.verbose:
        # Default behavior: print header only if more than one file
        print_header = total_files > 1
    
    # Open the file (or use stdin for "-")
    try:
        if file_path == "-":
            # Format the header for stdin
            file_desc = "standard input"
            file_obj = sys.stdin
        else:
            # Format the header for regular files
            file_desc = file_path
            file_obj = open(file_path, "r", errors="replace")
        
        # Print the header if needed
        if print_header:
            # Add a blank line between files (except for the first file)
            if file_number > 1:
                print()
            print(f"==> {file_desc} <==")
        
        # Process according to -c or -n option
        if options.bytes is not None:
            # Read and output bytes
            bytes_to_read = options.bytes
            
            if hasattr(file_obj, "buffer"):
                # For regular files and stdin that have a buffer
                data = file_obj.buffer.read(bytes_to_read)
                if hasattr(sys.stdout, "buffer"):
                    sys.stdout.buffer.write(data)
                else:
                    # Handle StringIO in tests
                    sys.stdout.write(data.decode('utf-8', errors='replace'))
            else:
                # For StringIO or other objects without a buffer
                data = file_obj.read(bytes_to_read)
                sys.stdout.write(data)
        else:
            # Read and output lines
            lines_to_read = options.lines
            line_count = 0
            for line in file_obj:
                if line_count >= lines_to_read:
                    break
                sys.stdout.write(line)
                line_count += 1
        
        # Close the file (if not stdin)
        if file_path != "-":
            file_obj.close()
        
        return 0
        
    except IOError as e:
        print(f"head: {file_path}: {e.strerror}", file=sys.stderr)
        return 1


def main(args):
    """Main function for the head command."""
    try:
        options = parse_args(args)
        
        # Determine files to process
        files = options.files
        if not files:
            # If no files specified, use stdin
            files = ["-"]
        
        # Process each file
        exit_code = 0
        for i, file_path in enumerate(files, 1):
            result = head_file(file_path, options, i, len(files))
            if result != 0:
                exit_code = result
        
        return exit_code
        
    except Exception as e:
        print(f"head: error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 