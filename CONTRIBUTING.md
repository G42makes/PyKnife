# Contributing to PyKnife

Thank you for your interest in contributing to PyKnife! This document provides guidelines and instructions for contributing.

## Adding a New Command

To add a new command to PyKnife, follow these steps:

### 1. Choose a Command

Choose a Linux command to implement. Prioritize common, useful commands with well-defined behavior. Check the project README to ensure it hasn't already been implemented.

### 2. Create Command Files

1. Create a new Python file in `src/commands/{command_name}.py`:
   - Use the template in `templates/command.py` as a starting point
   - Implement the functionality to match the behavior of the original command
   - Keep dependencies minimal, preferring the standard library

2. Add your command to `src/commands/__init__.py`:
   ```python
   __all__ = ["echo", ..., "{command_name}"]
   ```

### 3. Write Documentation

1. Create documentation in `docs/commands/{command_name}.md`:
   - Use the template in `templates/command_doc.md` as a starting point
   - Include a clear description, options, examples, and usage notes

### 4. Write Tests

1. Create a test file in `tests/test_{command_name}.py`:
   - Use the template in `templates/test_command.py` as a starting point
   - Write unit tests to verify all features and edge cases
   - Include reference tests to compare output with the actual system command

### 5. Update README

1. Add your command to the "Currently Implemented Commands" section of the README.md file

### 6. Test Your Implementation

1. Run the unit tests:
   ```bash
   python run_tests.py
   ```

2. On Linux systems, run the reference tests to compare with the actual command:
   ```bash
   python run_tests.py --reference
   ```

## Code Style Guidelines

- Follow PEP 8 style guidelines
- Use docstrings for all functions and classes
- Keep functions small and focused
- Add appropriate error handling
- Include comments for complex logic
- Write clear, descriptive variable and function names

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure they pass
5. Submit a pull request with a clear description of the changes

## Command Implementation Best Practices

1. **Command Line Behavior**: Ensure the command behaves like the original Linux command. Check the man pages for detailed behavior descriptions.

2. **Error Handling**: Handle errors and edge cases gracefully. Return appropriate exit codes.

3. **Output Format**: Match the output format of the original command as closely as possible.

4. **Dependencies**: Minimize dependencies. Use Python standard library modules whenever possible.

5. **Performance**: Consider performance implications, especially for commands that might handle large files.

6. **Testing**: Write comprehensive tests that cover both standard usage and edge cases.

Thank you for your contributions! 