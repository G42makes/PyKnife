#!/usr/bin/env python3
"""
cat command implementation.

The cat command concatenates files and prints them to standard output.
"""

import sys
import os
import argparse


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="cat",
        description="Concatenate files and print to standard output",
        usage=argparse.SUPPRESS
    )
    
    # File arguments
    parser.add_argument(
        "files", 
        nargs="*", 
        help="the files to concatenate"
    )
    
    # Line numbering options
    parser.add_argument(
        "-n", "--number", 
        action="store_true", 
        help="number all output lines"
    )
    
    parser.add_argument(
        "-b", "--number-nonblank", 
        action="store_true", 
        help="number nonempty output lines"
    )
    
    # Special character display options
    parser.add_argument(
        "-E", "--show-ends", 
        action="store_true", 
        help="display $ at end of each line"
    )
    
    parser.add_argument(
        "-T", "--show-tabs", 
        action="store_true", 
        help="display TAB characters as ^I"
    )
    
    parser.add_argument(
        "-A", "--show-all", 
        action="store_true", 
        help="equivalent to -vET"
    )
    
    # Show non-printing characters
    parser.add_argument(
        "-v", "--show-nonprinting", 
        action="store_true", 
        help="use ^ and M- notation, except for LFD and TAB"
    )
    
    return parser.parse_args(args)


def process_stream(stream, options, line_number=1):
    """
    Process a file stream with the specified options.
    
    Args:
        stream: The input stream to process
        options: Command options
        line_number: Starting line number for numbered output
        
    Returns:
        tuple: (Processed output, next line number)
    """
    result = []
    
    # Set display options
    show_ends = options.show_ends or options.show_all
    show_tabs = options.show_tabs or options.show_all
    show_nonprinting = options.show_nonprinting or options.show_all
    
    # Determine line numbering mode
    number_all = options.number
    number_nonblank = options.number_nonblank
    
    # If both numbering options are specified, -b takes precedence
    if number_all and number_nonblank:
        number_all = False
    
    # Process each line in the stream
    for line in stream:
        # Handle line numbering
        prefix = ""
        if number_nonblank and line.strip():
            prefix = f"{line_number:6d}\t"
            line_number += 1
        elif number_all:
            prefix = f"{line_number:6d}\t"
            line_number += 1
        
        # Process special characters
        processed_line = line
        
        if show_nonprinting:
            # Process non-printing characters
            processed_chars = []
            for char in processed_line:
                if char == '\t' and not show_tabs:  # Skip tabs if they'll be handled separately
                    processed_chars.append(char)
                elif char == '\n':  # Skip newlines
                    processed_chars.append(char)
                elif ord(char) < 32:  # Control characters
                    processed_chars.append(f"^{chr(ord(char) + 64)}")
                elif ord(char) == 127:  # DEL character
                    processed_chars.append("^?")
                elif ord(char) >= 128:  # High bit set
                    processed_chars.append(char)  # In a full implementation, would use M- notation
                else:
                    processed_chars.append(char)
            processed_line = ''.join(processed_chars)
        
        if show_tabs:
            processed_line = processed_line.replace('\t', '^I')
        
        if show_ends:
            # Remove existing newline to add $ at the end
            if processed_line.endswith('\n'):
                processed_line = processed_line[:-1] + '$\n'
            else:
                processed_line = processed_line + '$'
        
        # Add the processed line to the result
        result.append(prefix + processed_line)
    
    return ''.join(result), line_number


def cat_files(files, options):
    """
    Concatenate files and apply processing according to options.
    
    Args:
        files: List of file paths to concatenate
        options: Command options
    """
    # If no files are specified or if '-' is in files, read from stdin
    if not files or '-' in files:
        try:
            # Process stdin if no files are specified or if '-' is in files
            line_number = 1
            for file in files:
                if file == '-':
                    output, line_number = process_stream(sys.stdin, options, line_number)
                    sys.stdout.write(output)
                else:
                    with open(file, 'r', errors='replace') as f:
                        output, line_number = process_stream(f, options, line_number)
                        sys.stdout.write(output)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            return 130  # Standard exit code for SIGINT
    else:
        # Process each file
        line_number = 1
        for file in files:
            try:
                with open(file, 'r', errors='replace') as f:
                    output, line_number = process_stream(f, options, line_number)
                    sys.stdout.write(output)
            except IOError as e:
                print(f"cat: {file}: {e.strerror}", file=sys.stderr)
                return 1
    
    return 0


def main(args):
    """Main function for the cat command."""
    try:
        options = parse_args(args)
        return cat_files(options.files, options)
    except Exception as e:
        print(f"cat: error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 