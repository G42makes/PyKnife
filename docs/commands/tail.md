# tail

Output the last part of files.

## Synopsis

```
tail [OPTION]... [FILE]...
```

## Description

Print the last 10 lines of each FILE to standard output. If more than one FILE is specified,
precede each with a header giving the file name.

If no FILE is specified, or when FILE is `-`, `tail` reads from standard input.

The `tail` command is especially useful for monitoring log files in real-time using the `-f` option.

## Options

- `-c, --bytes=NUM`: Output the last NUM bytes. You can also use `-c +NUM` to output starting with byte NUM.
- `-f, --follow`: Output appended data as the file grows.
- `-n, --lines=NUM`: Output the last NUM lines instead of the last 10. You can also use `-n +NUM` to output starting with line NUM.
- `-q, --quiet, --silent`: Never print headers giving file names.
- `-v, --verbose`: Always print headers giving file names.

## Examples

Display the last 10 lines of a file:
```
tail file.txt
```

Display the last 5 lines of a file:
```
tail -n 5 file.txt
```

Display the last 20 bytes of a file:
```
tail -c 20 file.txt
```

Display all lines starting with line 15:
```
tail -n +15 file.txt
```

Monitor a file for changes:
```
tail -f /var/log/syslog
```

Display the last lines from multiple files:
```
tail file1.txt file2.txt
```

Display the last 10 lines from standard input:
```
cat file.txt | tail
```

## Exit Status

The tail command returns:
- 0 if successful
- 1 if an error occurs

## Notes

This implementation aims to be compatible with the GNU version of `tail`.

The `-f` option is particularly useful for watching log files in real-time. However, unlike the GNU 
implementation, this version doesn't support following multiple files simultaneously.

When used with multiple files, `tail` will display headers with the file names unless the `-q` option is used. 