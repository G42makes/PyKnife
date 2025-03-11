# cat

Concatenate files and print to standard output.

## Synopsis

```
cat [OPTION]... [FILE]...
```

## Description

Concatenates the contents of FILEs (or standard input if no files are provided or when
`-` is specified) to standard output.

If no FILE is specified, or when FILE is `-`, `cat` reads from standard input.

## Options

- `-A, --show-all`: Equivalent to `-ET`, display all non-printing characters
- `-b, --number-nonblank`: Number non-empty output lines, overrides `-n`
- `-E, --show-ends`: Display `$` at end of each line
- `-n, --number`: Number all output lines
- `-T, --show-tabs`: Display TAB characters as `^I`
- `-v, --show-nonprinting`: Use `^` and `M-` notation for non-printing characters (except LFD and TAB)

## Examples

Display the contents of a file:
```
cat file.txt
```

Display contents of multiple files:
```
cat file1.txt file2.txt
```

Display line numbers with the file contents:
```
cat -n file.txt
```

Display only non-blank line numbers:
```
cat -b file.txt
```

Display special characters:
```
cat -A file.txt
```

Read from standard input:
```
echo "Hello" | cat -
```

## Exit Status

The cat command returns:
- 0 if successful
- 1 if an error occurs
- 130 if interrupted with Ctrl+C (SIGINT)

## Notes

This implementation aims to be compatible with the GNU version of cat.

Unlike some versions of cat, this implementation does not have a `-s` option to squeeze
repeated empty lines. 