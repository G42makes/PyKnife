#!/usr/bin/env python3
"""
Reference tester for PyKnife.

This module provides functionality to test PyKnife command implementations
against the actual system commands as a reference.
"""

import os
import sys
import subprocess
import platform
import shlex
from io import StringIO


def is_command_available(command):
    """Check if a command is available on the system."""
    if platform.system() == "Windows":
        # Windows systems don't have most Linux commands natively
        return False
    
    try:
        # Try to run the command with --version or --help to see if it exists
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(
                [command, "--version"], 
                stdout=devnull, 
                stderr=devnull
            )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        try:
            # Some commands might not support --version, try --help
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(
                    [command, "--help"], 
                    stdout=devnull, 
                    stderr=devnull
                )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False


def run_system_command(command, args):
    """
    Run a system command with the given arguments and return its output.
    
    Args:
        command (str): The command to run (e.g., 'echo')
        args (list): List of arguments to pass to the command
        
    Returns:
        tuple: (stdout, stderr, return_code)
    """
    try:
        # Convert the command and args to a single string
        cmd = [command] + args
        
        # Run the command and capture output
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        return (
            process.stdout,
            process.stderr,
            process.returncode
        )
    except Exception as e:
        return ("", f"Error executing system command: {str(e)}", 1)


def compare_with_system(command, args, pyknife_func):
    """
    Compare the output of a PyKnife function with the system command.
    
    Args:
        command (str): The system command to compare against (e.g., 'echo')
        args (list): List of arguments to pass to both commands
        pyknife_func: The PyKnife function to call with the same args
        
    Returns:
        dict: Comparison results with keys:
            - 'match': True if outputs match, False otherwise
            - 'pyknife_output': Output from PyKnife implementation
            - 'system_output': Output from system command
            - 'system_stderr': Error output from system command
            - 'system_available': Whether the system command was available
            - 'system_return_code': Return code from system command
            - 'error': Error message, if any
    """
    result = {
        'match': False,
        'pyknife_output': "",
        'system_output': "",
        'system_stderr': "",
        'system_available': False,
        'system_return_code': 0,
        'error': None
    }
    
    # Check if system command is available
    result['system_available'] = is_command_available(command)
    if not result['system_available']:
        result['error'] = f"System command '{command}' is not available"
        return result
    
    # Capture PyKnife output
    old_stdout = sys.stdout
    sys.stdout = pyknife_output = StringIO()
    
    try:
        # Run PyKnife function
        pyknife_func(args)
        result['pyknife_output'] = pyknife_output.getvalue()
    except Exception as e:
        result['error'] = f"Error running PyKnife function: {str(e)}"
        sys.stdout = old_stdout
        return result
    finally:
        sys.stdout = old_stdout
    
    # Run system command
    system_stdout, system_stderr, return_code = run_system_command(command, args)
    result['system_output'] = system_stdout
    result['system_stderr'] = system_stderr
    result['system_return_code'] = return_code
    
    # Compare outputs, allowing for minor platform-specific differences
    # For example, different newline handling between platforms
    py_output = result['pyknife_output'].rstrip('\r\n')
    sys_output = result['system_output'].rstrip('\r\n')
    
    result['match'] = py_output == sys_output
    
    return result 