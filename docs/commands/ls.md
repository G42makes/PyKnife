# ls

List directory contents.

## Synopsis

```
ls [OPTION]... [FILE]...
```

## Description

List information about the FILE(s) (the current directory by default).
Sort entries alphabetically if none of `-S` or `-t` is specified.

## Options

### Display Options

- `-a`, `--all`: do not ignore entries starting with `.`
- `-l`: use a long listing format
- `-h`, `--human-readable`: with `-l`, print sizes in human readable format (e.g., 1K 234M 2G)
- `-R`, `--recursive`: list subdirectories recursively
- `-d`, `--directory`: list directories themselves, not their contents

### Sorting Options

- `-r`, `--reverse`: reverse order while sorting
- `-S`: sort by file size, largest first
- `-t`: sort by modification time, newest first

### Output Control

- `--color=WHEN`: colorize the output; WHEN can be 'never', 'auto', or 'always' (default is 'auto')

## Long Format

When the `-l` option is used, the output for each file includes:

- File type and permissions
- Number of hard links
- Owner name
- Group name
- File size in bytes (or human-readable with `-h`)
- Last modification time
- Filename

Example:
```
-rw-r--r-- 1 user group 4096 Jan 15 14:30 example.txt
```

## Examples

List files in the current directory:
```
ls
```

List all files, including hidden ones:
```
ls -a
```

Use long listing format:
```
ls -l
```

List files with human-readable sizes:
```
ls -lh
```

List directories themselves, not their contents:
```
ls -d */
```

List recursively:
```
ls -R
```

Sort files by modification time:
```
ls -lt
```

Sort files by size:
```
ls -lS
```

Reverse the sort order:
```
ls -lr
```

## Exit Status

The ls command returns:
- 0 if successful
- 1 if minor problems (e.g., cannot access subdirectory)
- 2 if serious trouble (e.g., cannot access command-line argument)

## Notes

This implementation aims to be compatible with the GNU version of ls, although
it does not implement all options of the original command.

Colorized output depends on terminal capabilities and may not work in all environments. 