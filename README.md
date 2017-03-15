# man helper

A tiny tool to show man page entries to a given cli.

## Requirements

Unix with `man`.

## Usage

```
./do.py [cli]
```

example:
```
$ ./do.py man -w man
cli: man -w man

keys:   -w, --where, --path, --location
descr:  Don't actually display the manual pages, but do print the location(s) of  the
        source nroff files that would be formatted.
```

## TODO

- git plugin
- handle concated options like `ls -al`