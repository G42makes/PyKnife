# PyKnife Commands

This directory contains the implementations of various Linux commands in Python.

## Command Structure

Each command should follow this general structure:

1. A Python module file named after the command (e.g., `echo.py`)
2. The module should provide at least:
   - `parse_args(args)`: Function to parse command line arguments
   - `main(args)`: Main function that implements the command logic

## Adding New Commands

1. Create a new file named after the command (e.g., `cat.py`)
2. Implement the command following the structure above
3. Add the command to `__init__.py`
4. Create documentation in `docs/commands/`
5. Create tests in `tests/`

See the CONTRIBUTING.md file in the root directory for detailed guidelines.

## Command Implementation Guidelines

1. **Match Original Behavior**: Aim to match the behavior of the original Linux command
2. **Minimize Dependencies**: Use Python standard library when possible
3. **Handle Errors Gracefully**: Proper error handling and appropriate exit codes
4. **Document Options**: All command-line options should be well-documented
5. **Test Thoroughly**: Both unit tests and reference tests against the system command

## Standard Exit Codes

Follow these standard exit codes:
- `0`: Success
- `1`: General errors
- `2`: Misuse of command (e.g., incorrect options)
- `>2`: Command-specific error codes 