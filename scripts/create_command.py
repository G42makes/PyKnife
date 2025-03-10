#!/usr/bin/env python3
"""
Command creator for PyKnife.

This script generates the necessary files for a new PyKnife command
based on templates.
"""

import os
import sys
import re
import shutil
import argparse


def camel_case(s):
    """Convert a string to CamelCase."""
    # Remove non-alphanumeric characters and convert to CamelCase
    words = re.findall(r'[a-zA-Z0-9]+', s)
    return ''.join(word.capitalize() for word in words)


def create_command(command_name, description=""):
    """
    Create all the necessary files for a new command.
    
    Args:
        command_name: The name of the command to create
        description: Brief description of the command
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(root_dir, 'templates')
    
    # Ensure the command name is valid
    if not re.match(r'^[a-z0-9_]+$', command_name):
        print(f"Error: Command name '{command_name}' is not valid. "
              "Use only lowercase letters, numbers, and underscores.")
        return 1
    
    # Check if command already exists
    command_file = os.path.join(root_dir, 'src', 'commands', f"{command_name}.py")
    if os.path.exists(command_file):
        print(f"Error: Command '{command_name}' already exists at '{command_file}'")
        return 1
    
    # Create command templates
    files_to_create = [
        {
            'template': os.path.join(templates_dir, 'command.py'),
            'destination': command_file,
            'replacements': {
                '{COMMAND_NAME}': command_name,
                '{BRIEF_DESCRIPTION}': description,
                '{DESCRIPTION}': description
            }
        },
        {
            'template': os.path.join(templates_dir, 'test_command.py'),
            'destination': os.path.join(root_dir, 'tests', f"test_{command_name}.py"),
            'replacements': {
                '{COMMAND_NAME}': command_name,
                'TestCommandName': f'Test{camel_case(command_name)}',
                'ReferenceCommandTests': f'Reference{camel_case(command_name)}Tests'
            }
        },
        {
            'template': os.path.join(templates_dir, 'command_doc.md'),
            'destination': os.path.join(root_dir, 'docs', 'commands', f"{command_name}.md"),
            'replacements': {
                '{COMMAND_NAME}': command_name,
                '{BRIEF_DESCRIPTION}': description,
                '{DETAILED_DESCRIPTION}': description,
                '{EXAMPLE_ARGS}': '[ARGS]',
                '{EXAMPLE_OPTION_ARGS}': '[OPTION_ARGS]',
                '{IMPLEMENTATION_NOTES}': 'This implementation aims to be compatible with the GNU version.'
            }
        }
    ]
    
    # Create each file
    for file_info in files_to_create:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(file_info['destination']), exist_ok=True)
        
        # Read template
        with open(file_info['template'], 'r') as f:
            content = f.read()
        
        # Apply replacements
        for placeholder, value in file_info['replacements'].items():
            content = content.replace(placeholder, value)
        
        # Write to destination
        with open(file_info['destination'], 'w') as f:
            f.write(content)
        
        print(f"Created {file_info['destination']}")
    
    # Update __init__.py
    init_file = os.path.join(root_dir, 'src', 'commands', '__init__.py')
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Find the __all__ line and update it
    if '__all__ = [' in content:
        all_pattern = r'__all__ = \[(.*?)\]'
        all_match = re.search(all_pattern, content, re.DOTALL)
        if all_match:
            existing_commands = all_match.group(1).strip()
            if existing_commands:
                # Add a comma if there are already commands
                if not existing_commands.endswith(','):
                    existing_commands += ','
                new_all = f'__all__ = [{existing_commands} "{command_name}"]'
            else:
                new_all = f'__all__ = ["{command_name}"]'
            
            content = re.sub(all_pattern, new_all, content, flags=re.DOTALL)
    
    with open(init_file, 'w') as f:
        f.write(content)
    
    print(f"Updated {init_file}")
    print(f"\nCommand '{command_name}' created successfully!")
    print("\nNext steps:")
    print(f"1. Implement the command logic in {command_file}")
    print(f"2. Write tests in tests/test_{command_name}.py")
    print(f"3. Complete the documentation in docs/commands/{command_name}.md")
    print("4. Add the command to the 'Currently Implemented Commands' section in README.md")
    
    return 0


def main():
    """Parse command line arguments and create the command files."""
    parser = argparse.ArgumentParser(description="Create a new PyKnife command")
    parser.add_argument('command_name', help="Name of the command to create")
    parser.add_argument('-d', '--description', help="Brief description of the command", default="")
    
    args = parser.parse_args()
    
    return create_command(args.command_name, args.description)


if __name__ == "__main__":
    sys.exit(main()) 