#!/usr/bin/env python3
"""
touch command implementation.

The touch command updates the modification and access times of files.
If the file doesn't exist, it creates an empty file.
"""

import sys
import os
import argparse
import time
import datetime


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="touch",
        description="Update the access and modification times of each FILE to the current time.",
        usage=argparse.SUPPRESS
    )
    
    # File arguments
    parser.add_argument(
        "files", 
        nargs="+", 
        help="the files to touch"
    )
    
    # Change only access time
    parser.add_argument(
        "-a", 
        action="store_true", 
        help="change only the access time"
    )
    
    # Do not create files
    parser.add_argument(
        "-c", "--no-create", 
        action="store_true", 
        help="do not create any files"
    )
    
    # Change only modification time
    parser.add_argument(
        "-m", 
        action="store_true", 
        help="change only the modification time"
    )
    
    # Use reference file's timestamps
    parser.add_argument(
        "-r", "--reference", 
        metavar="FILE",
        help="use this file's times instead of current time"
    )
    
    # Use a specific date/time
    parser.add_argument(
        "-d", "--date", 
        metavar="STRING",
        help="parse STRING and use it instead of current time"
    )
    
    # Use a specific date/time (timestamp format)
    parser.add_argument(
        "-t", 
        metavar="STAMP",
        help="use [[CC]YY]MMDDhhmm[.ss] instead of current time"
    )
    
    return parser.parse_args(args)


def parse_date_string(date_string):
    """
    Parse a date string in a format accepted by the -d option.
    
    This is a simplified version that handles common formats.
    For a full implementation, consider using dateutil.parser.
    
    Returns:
        Tuple of (atime, mtime) as timestamps
    """
    try:
        # Try a basic ISO format first (YYYY-MM-DD HH:MM:SS)
        dt = datetime.datetime.fromisoformat(date_string.replace('T', ' '))
        timestamp = dt.timestamp()
        return (timestamp, timestamp)
    except ValueError:
        # Handle some common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",  # 2023-01-30 15:30:45
            "%Y-%m-%d",           # 2023-01-30
            "%b %d %H:%M:%S %Y",  # Jan 30 15:30:45 2023
            "%b %d %Y",           # Jan 30 2023
        ]
        
        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(date_string, fmt)
                timestamp = dt.timestamp()
                return (timestamp, timestamp)
            except ValueError:
                continue
        
        # If all else fails, raise an error
        raise ValueError(f"Invalid date format: {date_string}")


def parse_timestamp(timestamp_str):
    """
    Parse a timestamp in the format [[CC]YY]MMDDhhmm[.ss]
    
    Returns:
        Tuple of (atime, mtime) as timestamps
    """
    # Remove any dots and split seconds if present
    seconds = 0
    if '.' in timestamp_str:
        parts = timestamp_str.split('.')
        timestamp_str = parts[0]
        if len(parts) > 1 and parts[1].isdigit():
            seconds = int(parts[1])
    
    # Determine the format based on length
    length = len(timestamp_str)
    year = None
    month = None
    day = None
    hour = None
    minute = None
    
    if length == 8:  # MMDDhhmm
        month = int(timestamp_str[0:2])
        day = int(timestamp_str[2:4])
        hour = int(timestamp_str[4:6])
        minute = int(timestamp_str[6:8])
        year = datetime.datetime.now().year
    elif length == 10:  # YYMMDDhhmm
        year = 2000 + int(timestamp_str[0:2])
        month = int(timestamp_str[2:4])
        day = int(timestamp_str[4:6])
        hour = int(timestamp_str[6:8])
        minute = int(timestamp_str[8:10])
    elif length == 12:  # CCYYMMDDhhmm
        year = int(timestamp_str[0:4])
        month = int(timestamp_str[4:6])
        day = int(timestamp_str[6:8])
        hour = int(timestamp_str[8:10])
        minute = int(timestamp_str[10:12])
    else:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}")
    
    # Create a datetime object and convert to timestamp
    dt = datetime.datetime(year, month, day, hour, minute, seconds)
    timestamp = dt.timestamp()
    return (timestamp, timestamp)


def touch_file(file_path, times=None, only_access=False, only_modification=False, no_create=False):
    """
    Update the access and modification times of the specified file.
    If the file doesn't exist, create it unless no_create is True.
    
    Args:
        file_path: Path to the file to touch
        times: Tuple of (atime, mtime) to use, or None for current time
        only_access: Only update access time if True
        only_modification: Only update modification time if True
        no_create: Don't create the file if it doesn't exist
        
    Returns:
        True if successful, False otherwise
    """
    # Default to current time if not specified
    if times is None:
        current_time = time.time()
        times = (current_time, current_time)
    
    # Handle the case where file doesn't exist
    if not os.path.exists(file_path):
        if no_create:
            return True  # Skip silently as per touch behavior
        
        try:
            # Create an empty file
            with open(file_path, 'a'):
                pass
        except (IOError, PermissionError) as e:
            print(f"touch: cannot touch '{file_path}': {e.strerror}", file=sys.stderr)
            return False
    
    # Determine which times to change
    if only_access and not only_modification:
        # Keep the current mtime
        mtime = os.path.getmtime(file_path)
        atime = times[0]
    elif only_modification and not only_access:
        # Keep the current atime
        atime = os.path.getatime(file_path)
        mtime = times[1]
    else:
        # Change both times
        atime, mtime = times
    
    try:
        # Update the file times
        os.utime(file_path, (atime, mtime))
        return True
    except (IOError, PermissionError) as e:
        print(f"touch: cannot touch '{file_path}': {e.strerror}", file=sys.stderr)
        return False


def main(args):
    """Main function for the touch command."""
    try:
        options = parse_args(args)
        
        # Determine the timestamps to use
        times = None  # Default to current time
        
        if options.reference:
            # Use reference file's timestamps
            try:
                atime = os.path.getatime(options.reference)
                mtime = os.path.getmtime(options.reference)
                times = (atime, mtime)
            except (FileNotFoundError, IOError) as e:
                print(f"touch: failed to get attributes of '{options.reference}': {str(e)}", file=sys.stderr)
                return 1
        elif options.date:
            # Use date string
            try:
                times = parse_date_string(options.date)
            except ValueError as e:
                print(f"touch: {str(e)}", file=sys.stderr)
                return 1
        elif options.t:
            # Use timestamp
            try:
                times = parse_timestamp(options.t)
            except ValueError as e:
                print(f"touch: {str(e)}", file=sys.stderr)
                return 1
        
        # Process each file
        exit_code = 0
        for file_path in options.files:
            result = touch_file(
                file_path, 
                times=times, 
                only_access=options.a, 
                only_modification=options.m, 
                no_create=options.no_create
            )
            if not result:
                exit_code = 1
        
        return exit_code
        
    except Exception as e:
        print(f"touch: error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 