#!/usr/bin/env python3
"""
wc command implementation.

The wc command counts the number of lines, words, and bytes in files.
"""

import sys
import os
import argparse


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="wc",
        description="Print newline, word, and byte counts for each file",
        usage=argparse.SUPPRESS
    )
    
    # File arguments
    parser.add_argument(
        "files", 
        nargs="*", 
        help="the files to process"
    )
    
    # Counting options
    parser.add_argument(
        "-c", "--bytes", 
        action="store_true", 
        help="print the byte counts"
    )
    
    parser.add_argument(
        "-m", "--chars", 
        action="store_true", 
        help="print the character counts"
    )
    
    parser.add_argument(
        "-l", "--lines", 
        action="store_true", 
        help="print the newline counts"
    )
    
    parser.add_argument(
        "-w", "--words", 
        action="store_true", 
        help="print the word counts"
    )
    
    parser.add_argument(
        "-L", "--max-line-length", 
        action="store_true", 
        help="print the maximum display width"
    )
    
    return parser.parse_args(args)


def count_file(file_path):
    """
    Count lines, words, characters, and bytes in a file.
    
    Args:
        file_path: Path to the file or "-" for stdin.
        
    Returns:
        dict: A dictionary with the following keys:
            'lines': Number of lines
            'words': Number of words
            'chars': Number of characters
            'bytes': Number of bytes
            'max_line_length': Length of the longest line
    """
    try:
        # Open the file (or use stdin for "-")
        if file_path == "-":
            file_obj = sys.stdin
        else:
            file_obj = open(file_path, "r", errors="replace")
        
        # Initialize counters
        lines = 0
        words = 0
        chars = 0
        max_line_length = 0
        
        # Read the file line by line
        for line in file_obj:
            lines += 1
            chars += len(line)
            words += len(line.split())
            max_line_length = max(max_line_length, len(line.rstrip('\n')))
        
        # Close the file (if not stdin)
        if file_path != "-":
            file_obj.close()
            
            # For bytes, we need to reopen in binary mode to get the actual byte count
            with open(file_path, "rb") as f:
                bytes_count = len(f.read())
        else:
            # For stdin, we already processed it, so bytes == chars
            bytes_count = chars
        
        return {
            'lines': lines,
            'words': words,
            'chars': chars,
            'bytes': bytes_count,
            'max_line_length': max_line_length
        }
    
    except IOError as e:
        print(f"wc: {file_path}: {e.strerror}", file=sys.stderr)
        return None


def format_output(file_counts, file_path, options):
    """
    Format the output for a file according to the options.
    
    Args:
        file_counts: Dictionary with counts for the file.
        file_path: Path to the file (for display).
        options: Command options.
        
    Returns:
        str: The formatted output line.
    """
    output_parts = []
    
    # Determine which counts to display
    show_lines = options.lines
    show_words = options.words
    show_bytes = options.bytes
    show_chars = options.chars
    show_max_line_length = options.max_line_length
    
    # If no count options specified, show default (lines, words, bytes)
    if not (show_lines or show_words or show_bytes or show_chars or show_max_line_length):
        show_lines = show_words = show_bytes = True
    
    # Add each count to the output
    if show_lines:
        output_parts.append(f"{file_counts['lines']:8d}")
    
    if show_words:
        output_parts.append(f"{file_counts['words']:8d}")
    
    if show_chars:
        output_parts.append(f"{file_counts['chars']:8d}")
    
    if show_bytes:
        output_parts.append(f"{file_counts['bytes']:8d}")
    
    if show_max_line_length:
        output_parts.append(f"{file_counts['max_line_length']:8d}")
    
    # Add the file name (or stdin indicator)
    if file_path == "-":
        file_display = ""  # No filename for stdin in default mode
    else:
        file_display = f" {file_path}"
    
    return "".join(output_parts) + file_display


def wc_files(files, options):
    """
    Process files according to wc options and print results.
    
    Args:
        files: List of file paths to process.
        options: Command options.
        
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    # Initialize counters for totals
    total_lines = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0
    total_max_line_length = 0
    
    # Track if any files were successfully processed
    any_success = False
    
    # Process each file
    for file_path in files:
        file_counts = count_file(file_path)
        
        if file_counts is None:
            continue  # Error occurred
        
        # Update totals
        total_lines += file_counts['lines']
        total_words += file_counts['words']
        total_chars += file_counts['chars']
        total_bytes += file_counts['bytes']
        total_max_line_length = max(total_max_line_length, file_counts['max_line_length'])
        
        # Print the results for this file
        print(format_output(file_counts, file_path, options))
        
        any_success = True
    
    # If multiple files were processed, print totals
    if len(files) > 1 and any_success:
        total_counts = {
            'lines': total_lines,
            'words': total_words,
            'chars': total_chars,
            'bytes': total_bytes,
            'max_line_length': total_max_line_length
        }
        print(format_output(total_counts, "total", options))
    
    return 0 if any_success else 1


def main(args):
    """Main function for the wc command."""
    try:
        options = parse_args(args)
        
        # Determine files to process
        files = options.files
        if not files:
            # If no files specified, use stdin
            files = ["-"]
        
        return wc_files(files, options)
        
    except Exception as e:
        print(f"wc: error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 