# mkdir

Create directories.

## Synopsis

```
mkdir [OPTION]... DIRECTORY...
```

## Description

Create the DIRECTORY(ies), if they do not already exist.

Mandatory arguments to long options are mandatory for short options too.

## Options

- `-m`, `--mode=MODE`: set file mode (as in chmod), not a=rwx - umask
- `-p`, `--parents`: make parent directories as needed, no error if existing
- `-v`, `--verbose`: print a message for each created directory

## Mode

The default mode is 0777 (octal), which means all access permissions. 
This is modified by the process's umask value.

The specified mode can be in octal (with leading zero) or decimal.

For example:
- `0755` (octal) sets rwxr-xr-x permissions
- `0644` (octal) sets rw-r--r-- permissions

## Examples

Create a directory:
```
mkdir mydir
```

Create multiple directories:
```
mkdir dir1 dir2 dir3
```

Create nested directories:
```
mkdir -p parent/child/grandchild
```

Create a directory with specific permissions:
```
mkdir -m 0755 mydir
```

Create directories verbosely:
```
mkdir -v dir1 dir2
```

## Exit Status

The mkdir command returns:
- 0 if all directories were successfully created
- 1 if any errors occurred

## Notes

This implementation aims to be compatible with the GNU version of mkdir.

The handling of permissions can vary due to each system's umask settings. 
The actual permissions created will be: `(mode & ~umask)`.

Unlike symbolic mode notation (e.g., "u+rwx,g+rx,o+rx") in chmod, 
mkdir only accepts numeric mode specifications. 