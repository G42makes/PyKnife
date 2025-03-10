#!/usr/bin/env python3
"""
Echo command implementation.

The echo command displays a line of text. It follows the behavior of the
POSIX echo utility.
"""

import sys
import argparse


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="echo",
        description="Display a line of text",
        # Don't print usage when there's an error
        usage=argparse.SUPPRESS
    )
    
    # -n suppresses the trailing newline
    parser.add_argument(
        "-n", 
        action="store_true", 
        help="do not output the trailing newline"
    )
    
    # -e enables interpretation of backslash escapes
    parser.add_argument(
        "-e", 
        action="store_true", 
        help="enable interpretation of backslash escapes"
    )
    
    # -E disables interpretation of backslash escapes (default)
    parser.add_argument(
        "-E", 
        action="store_true", 
        help="disable interpretation of backslash escapes (default)"
    )
    
    # All other arguments are treated as strings to print
    parser.add_argument(
        "strings", 
        nargs="*", 
        help="the strings to print"
    )
    
    return parser.parse_args(args)


def process_escapes(text):
    """Process backslash escape sequences in the text."""
    # Define escape sequences similar to the Linux echo command
    escapes = {
        "\\\\": "\\",   # backslash
        "\\a": "\a",    # alert (BEL)
        "\\b": "\b",    # backspace
        "\\c": "",      # produce no further output
        "\\e": "\x1b",  # escape
        "\\f": "\f",    # form feed
        "\\n": "\n",    # new line
        "\\r": "\r",    # carriage return
        "\\t": "\t",    # horizontal tab
        "\\v": "\v",    # vertical tab
    }
    
    # Replace each escape sequence
    result = ""
    i = 0
    while i < len(text):
        if text[i:i+2] == "\\c":
            # Stop processing at \c
            break
        elif text[i:i+2] in escapes:
            result += escapes[text[i:i+2]]
            i += 2
        else:
            result += text[i]
            i += 1
            
    return result


def main(args):
    """Main function for the echo command."""
    parsed_args = parse_args(args)
    
    # Join all strings with a space
    output = " ".join(parsed_args.strings)
    
    # Determine whether to process escape sequences
    # We need to honor the order of -e and -E flags
    process_escapes_flag = False
    
    # Check the order of -e and -E flags
    e_index = -1 if "-e" not in args else args.index("-e")
    E_index = -1 if "-E" not in args else args.index("-E")
    
    # Process escapes if:
    # 1. -e is present and -E is not, OR
    # 2. Both -e and -E are present, but -e comes after -E
    if parsed_args.e and (not parsed_args.E or (e_index > E_index)):
        process_escapes_flag = True
    
    # Apply escape processing if needed
    if process_escapes_flag:
        output = process_escapes(output)
    
    # Determine if we should add a newline
    end = "" if parsed_args.n else "\n"
    
    # Print the output
    print(output, end=end)
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
