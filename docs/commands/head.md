# head

Output the first part of files.

## Synopsis

```
head [OPTION]... [FILE]...
```

## Description

Print the first 10 lines of each FILE to standard output. If more than one FILE is specified,
precede each with a header giving the file name.

If no FILE is specified, or when FILE is `-`, head reads from standard input.

## Options

- `-c, --bytes=NUM`: Print the first NUM bytes of each file.
- `-n, --lines=NUM`: Print the first NUM lines instead of the first 10.
- `-q, --quiet, --silent`: Never print headers giving file names.
- `-v, --verbose`: Always print headers giving file names.

## Examples

Display the first 10 lines of a file:
```
head file.txt
```

Display the first 5 lines of a file:
```
head -n 5 file.txt
```

Display the first 20 bytes of a file:
```
head -c 20 file.txt
```

Display headers for multiple files:
```
head file1.txt file2.txt
```

Display the first 10 lines from standard input:
```
echo -e "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\nLine 9\nLine 10\nLine 11" | head
```

## Exit Status

The head command returns:
- 0 if successful
- 1 if an error occurs

## Notes

This implementation aims to be compatible with the GNU version of head.

For large files, the `-c` option is more efficient than `-n` when you need to read only 
a small portion of the file. 