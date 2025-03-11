# wc

Print newline, word, and byte counts for each file.

## Synopsis

```
wc [OPTION]... [FILE]...
```

## Description

The `wc` command displays the number of lines, words, and bytes contained in each input file, or standard input if no file is specified.

A word is defined as a non-zero-length sequence of characters delimited by whitespace.

If more than one file is specified, `wc` also outputs a line with the total counts.

## Options

- `-c, --bytes`: Print the byte counts.
- `-m, --chars`: Print the character counts.
- `-l, --lines`: Print the newline counts.
- `-w, --words`: Print the word counts.
- `-L, --max-line-length`: Print the length of the longest line.

If no options are specified, `wc` displays the line, word, and byte counts in that order.

## Examples

Count lines, words, and bytes in a file:
```
wc file.txt
```

Count only lines:
```
wc -l file.txt
```

Count words in multiple files:
```
wc -w file1.txt file2.txt
```

Count lines from standard input:
```
cat file.txt | wc -l
```

Show character count and maximum line length:
```
wc -m -L file.txt
```

## Exit Status

The wc command returns:
- 0 if successful
- 1 if an error occurs

## Notes

This implementation aims to be compatible with the GNU version of `wc`.

The difference between the byte count (`-c`) and character count (`-m`) is relevant only for files containing multi-byte characters (like UTF-8). For ASCII files, these counts will be identical. 