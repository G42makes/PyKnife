# pwd

Print the current working directory.

## Synopsis

```
pwd [OPTION]...
```

## Description

Print the full filename of the current working directory.

## Options

- `-P`: Avoid all symlinks and print the physical directory structure (the actual location in the filesystem)
- `-L`: Follow symlinks (default behavior)

## Examples

Basic usage:
```
pwd
/home/user/documents
```

Print the physical directory (avoid symlinks):
```
pwd -P
/home/user/documents
```

## Exit Status

The pwd command returns:
- 0 if successful
- non-zero if an error occurs (e.g., cannot access current directory)

## Notes

This implementation aims to be compatible with the GNU version of pwd. 

The `-P` option is useful when the current directory contains symlinks, as it will show the "real" physical path rather than the path that includes symlinks. 