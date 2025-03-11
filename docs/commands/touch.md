# touch

Update the access and modification times of each FILE to the current time.

## Synopsis

```
touch [OPTION]... FILE...
```

## Description

Update the access and modification timestamps of each FILE to the current time.

A FILE argument that does not exist is created empty, unless -c is supplied.

If a FILE is `-`, the touch command will fail.

## Options

- `-a`: change only the access time
- `-c`, `--no-create`: do not create any files
- `-d`, `--date=STRING`: parse STRING and use it instead of current time
- `-m`: change only the modification time
- `-r`, `--reference=FILE`: use this file's times instead of current time
- `-t STAMP`: use [[CC]YY]MMDDhhmm[.ss] instead of current time

## Date Formats

The `-d` option accepts various date formats, including:

- ISO 8601 format: `2023-01-30T15:30:45` or `2023-01-30 15:30:45`
- Simple date: `2023-01-30`
- Standard format: `Jan 30 15:30:45 2023`
- Month and year: `Jan 30 2023`

The `-t` option requires a specific timestamp format:

- `MMDDhhmm`: month, day, hour, minute (current year)
- `YYMMDDhhmm`: 2-digit year, month, day, hour, minute
- `CCYYMMDDhhmm`: 4-digit year, month, day, hour, minute
- Any of the above with `.ss` appended for seconds precision

## Examples

Create an empty file or update timestamps of an existing file:
```
touch file.txt
```

Update only the access time:
```
touch -a file.txt
```

Update only the modification time:
```
touch -m file.txt
```

Don't create file if it doesn't exist:
```
touch -c nonexistent.txt
```

Use a reference file's timestamps:
```
touch -r reference.txt target.txt
```

Set specific timestamps using a date string:
```
touch -d "2023-01-30 15:30:45" file.txt
```

Set specific timestamps using the timestamp format:
```
touch -t 202301301530.45 file.txt
```

Update multiple files at once:
```
touch file1.txt file2.txt file3.txt
```

## Exit Status

The touch command returns:
- 0 if all files were successfully updated
- 1 if any errors occurred

## Notes

This implementation aims to be compatible with the GNU version of touch.

Unlike some other commands, touch generally doesn't produce any output when successful.

The implementation provides date parsing for common formats, but may not support all formats accepted by the GNU version. 