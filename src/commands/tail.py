#!/usr/bin/env python3
"""
tail command implementation.

The tail command outputs the last part of files.
"""

import sys
import os
import argparse
import time
import signal


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="tail",
        description="Output the last part of files",
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
        type=str,
        default="10", 
        help="output the last NUM lines, instead of the last 10; or use -n +NUM to output starting with line NUM"
    )
    
    parser.add_argument(
        "-c", "--bytes", 
        type=str, 
        help="output the last NUM bytes; or use -c +NUM to output starting with byte NUM"
    )
    
    parser.add_argument(
        "-f", "--follow", 
        action="store_true", 
        help="output appended data as the file grows"
    )
    
    parser.add_argument(
        "-q", "--quiet", "--silent", 
        action="store_true", 
        help="never output headers giving file names"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="always output headers giving file names"
    )
    
    return parser.parse_args(args)


def get_starting_position(option_value, file_size):
    """
    Determine the starting position based on the option value.
    
    Args:
        option_value: String containing the option value (e.g., "10" or "+10")
        file_size: Total size of the file in bytes/lines
        
    Returns:
        int: Starting position. Negative means "from the end".
    """
    if option_value.startswith('+'):
        # +NUM means start at line/byte NUM (1-based)
        try:
            position = int(option_value[1:]) - 1  # 0-based
            if position < 0:
                position = 0
            return position
        except ValueError:
            # Invalid number, use default
            return -10
    else:
        # NUM means last NUM lines/bytes
        try:
            # Negative number means "from the end"
            count = int(option_value)
            if count < 0:
                count = -count
            return -count
        except ValueError:
            # Invalid number, use default
            return -10


def tail_file_by_lines(file_path, start_line, max_lines=None):
    """
    Read a file and return the specified lines.
    
    Args:
        file_path: Path to the file to read
        start_line: If negative, read that many lines from the end.
                   If positive, start at that line (0-based).
        max_lines: Maximum number of lines to read (optional)
        
    Returns:
        list: Lines from the file
    """
    if file_path == "-":
        # For stdin, we need to read all lines
        lines = sys.stdin.readlines()
    else:
        with open(file_path, "r", errors="replace") as f:
            lines = f.readlines()
    
    total_lines = len(lines)
    
    if start_line < 0:
        # Negative start_line means "last N lines"
        start_index = max(0, total_lines + start_line)
    else:
        # Positive means "starting at line N"
        start_index = min(start_line, total_lines)
    
    if max_lines is not None:
        # Limit to max_lines
        end_index = min(start_index + max_lines, total_lines)
    else:
        # Read to the end
        end_index = total_lines
    
    return lines[start_index:end_index]


def tail_file_by_bytes(file_path, start_byte, max_bytes=None):
    """
    Read a file and return the specified bytes.
    
    Args:
        file_path: Path to the file to read
        start_byte: If negative, read that many bytes from the end.
                   If positive, start at that byte (0-based).
        max_bytes: Maximum number of bytes to read (optional)
        
    Returns:
        bytes: Bytes from the file
    """
    if file_path == "-":
        # For stdin, we need to read all bytes
        content = sys.stdin.buffer.read()
    else:
        with open(file_path, "rb") as f:
            content = f.read()
    
    total_bytes = len(content)
    
    if start_byte < 0:
        # Negative start_byte means "last N bytes"
        start_index = max(0, total_bytes + start_byte)
    else:
        # Positive means "starting at byte N"
        start_index = min(start_byte, total_bytes)
    
    if max_bytes is not None:
        # Limit to max_bytes
        end_index = min(start_index + max_bytes, total_bytes)
    else:
        # Read to the end
        end_index = total_bytes
    
    return content[start_index:end_index]


def follow_file(file_path, callback):
    """
    Follow a file and call callback when new data is available.
    
    Args:
        file_path: Path to the file to follow
        callback: Function to call with new data
    """
    # Get the initial file size
    try:
        file_size = os.path.getsize(file_path)
    except OSError:
        # File might not exist yet
        file_size = 0
    
    # Open the file and seek to the end
    with open(file_path, "rb") as f:
        f.seek(file_size)
        
        # Set up signal handler for Ctrl+C
        stop_following = [False]
        
        def signal_handler(sig, frame):
            stop_following[0] = True
        
        original_handler = signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while not stop_following[0]:
                # Check for new data
                line = f.readline()
                if line:
                    # We have new data
                    callback(line)
                else:
                    # No new data, wait a bit
                    time.sleep(0.1)
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, original_handler)


def process_file(file_path, options, file_number, total_files):
    """
    Process a single file according to the options.
    
    Args:
        file_path: Path to the file to process
        options: Command options
        file_number: Current file number (for header output)
        total_files: Total number of files (for header output)
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Determine whether to print headers
    print_header = True
    if options.quiet:
        print_header = False
    elif not options.verbose:
        # Default behavior: print header only if more than one file
        print_header = total_files > 1
    
    # Print the header if needed
    if print_header:
        # Add a blank line between files (except for the first file)
        if file_number > 1:
            print()
        file_desc = "standard input" if file_path == "-" else file_path
        print(f"==> {file_desc} <==")
    
    try:
        # Determine how to process the file
        if options.bytes is not None:
            # Process by bytes
            start_byte = get_starting_position(options.bytes, 0)
            content = tail_file_by_bytes(file_path, start_byte)
            
            # Write to stdout
            if hasattr(sys.stdout, "buffer"):
                sys.stdout.buffer.write(content)
            else:
                # For testing or other environments that don't have a buffer
                sys.stdout.write(content.decode("utf-8", errors="replace"))
        else:
            # Process by lines
            start_line = get_starting_position(options.lines, 0)
            lines = tail_file_by_lines(file_path, start_line)
            
            # Write to stdout
            for line in lines:
                sys.stdout.write(line)
        
        # Handle follow mode (-f)
        if options.follow and file_path != "-":
            # Print a newline if the last line doesn't end with one
            if lines and not lines[-1].endswith("\n"):
                print()
            
            # Define the callback for new data
            def print_new_data(data):
                try:
                    text = data.decode("utf-8", errors="replace")
                    sys.stdout.write(text)
                    sys.stdout.flush()
                except IOError:
                    # Handle broken pipe or other IO errors
                    return
            
            # Start following the file
            follow_file(file_path, print_new_data)
        
        return 0
        
    except IOError as e:
        print(f"tail: {file_path}: {e.strerror}", file=sys.stderr)
        return 1


def main(args):
    """Main function for the tail command."""
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
            result = process_file(file_path, options, i, len(files))
            if result != 0:
                exit_code = result
            
            # If we're following a file, don't process any more files
            if options.follow and i < len(files):
                print(f"tail: warning: following multiple files is not supported in this implementation", file=sys.stderr)
                break
        
        return exit_code
        
    except Exception as e:
        print(f"tail: error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 