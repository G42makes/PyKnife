# PyKnife

A Python implementation of common Linux CLI tools.

## Overview

PyKnife provides pure Python implementations of common Linux command-line tools. It aims to be a fully functional alternative to traditional Linux utilities, with minimal dependencies.

## Features

- Pure Python 3 implementation
- Minimal dependencies (uses primarily the Python standard library)
- Commands match the behavior of their Linux counterparts
- BusyBox-style invocation through symlinks

## Currently Implemented Commands

- `cat` - Concatenate files and print to standard output
- `echo` - Display a line of text
- `head` - Output the first part of files
- `ls` - List directory contents
- `mkdir` - Create directories
- `pwd` - Print the current working directory
- `tail` - Output the last part of files
- `touch` - Update the access and modification times of files
- `wc` - Print newline, word, and byte counts for each file

## Installation

No installation required. Simply clone the repository and run the CLI directly:

```bash
git clone https://github.com/yourusername/PyKnife.git
cd PyKnife
python src/cli.py echo "Hello, World!"
```

## Usage

PyKnife can be used in two ways:

### 1. Specifying Command as an Argument

```
python src/cli.py COMMAND [ARGS]
```

For example:
```bash
python src/cli.py echo "Hello, World!"
python src/cli.py pwd
```

### 2. BusyBox-Style Symlink Invocation

You can set up symlinks to run commands directly, similar to BusyBox:

```bash
# Setup symlinks in a directory (e.g., ~/bin)
python scripts/setup_symlinks.py ~/bin

# Now you can run commands directly
~/bin/echo "Hello, World!"
~/bin/pwd
```

On Windows, use:
```
python scripts\setup_symlinks.py .\bin --py
python .\bin\echo.py "Hello, World!"
```

This symlink-based approach allows you to use PyKnife commands just like their native counterparts!

## Documentation

See the [documentation](docs/commands/) for details on each command.

## Testing

PyKnife includes a comprehensive test suite to ensure each command works as expected.

### Basic Testing

To run all tests:

```bash
python run_tests.py
```

You can also run individual tests:

```bash
python -m unittest tests/test_echo.py
```

### Reference Testing

PyKnife can also test its implementations against the actual system commands to verify compatibility:

```bash
python run_tests.py --reference
```

Reference tests will:
- Compare PyKnife's output with the output of the corresponding system command
- Skip tests for commands or options not available on your system
- Show detailed information about any differences

These tests are particularly useful on Linux systems where the actual commands are available.

## Development

### Creating a New Command

The easiest way to create a new command is to use the command creator script:

```bash
python scripts/create_command.py command_name -d "Brief description"
```

This will:
1. Create the command implementation file
2. Create a test file
3. Create documentation
4. Update the `__init__.py` file

Then you can implement the command following the guidance in the created files.

### Development Workflow

PyKnife provides templates and helper tools to streamline development:

- Templates for new commands in `templates/`
- Command creation script in `scripts/`
- Contributing guidelines in `CONTRIBUTING.md`

See the [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidance on adding new commands.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. When contributing, please follow our [branch naming convention](CONTRIBUTING.md#branch-naming-convention) (e.g., `command/cat` for adding a new command).

Please note that this project was developed with significant AI assistance. If you use AI tools for your contributions, please follow the guidelines in [AI Contributions](ai.md).

## License

See the [LICENSE](LICENSE) file for details. 