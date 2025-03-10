# echo

Display a line of text.

## Synopsis

```
echo [OPTION]... [STRING]...
```

## Description

Echo the STRING(s) to standard output.

## Options

- `-n`: do not output the trailing newline
- `-e`: enable interpretation of backslash escapes
- `-E`: disable interpretation of backslash escapes (default)

## Escape Sequences

The following escape sequences are recognized when the `-e` option is used:

- `\\`: backslash
- `\a`: alert (BEL)
- `\b`: backspace
- `\c`: produce no further output
- `\e`: escape character
- `\f`: form feed
- `\n`: new line
- `\r`: carriage return
- `\t`: horizontal tab
- `\v`: vertical tab

## Examples

Basic usage:
```
echo Hello, World!
```

Without newline:
```
echo -n "No newline"
```

With escape sequences:
```
echo -e "Tab: \t Newline: \n"
```

## Exit Status

The echo command returns:
- 0 if successful
- non-zero if an error occurs

## Notes

This implementation aims to be compatible with the GNU version of echo.
