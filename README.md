# man helper

A tiny tool to show man page entries to a given CLI.

In unix bash there are often long commands and it is not directly clear what
they are doing. Let's take `netstat -tulpen` as an example. The program itself is called
`netstat` and `-tulpen` are some parameters which we want to know what they
are actually doing. The usual way is to search in `netstat --help` or in `man netstat`.
The output of `netstat --help` looks like this:
```
[...]
        -l, --listening          display listening server sockets
        -a, --all                display all sockets (default: connected)
        -F, --fib                display Forwarding Information Base (default)
        -C, --cache              display routing cache instead of FIB
[...]
```
The output of `man netstat` looks like this:
```
[...]
   -l, --listening
       Show only listening sockets.  (These are omitted by default.)

   -a, --all
       Show both listening and non-listening sockets.  With the --interfaces
       option, show interfaces that are not up

   -F
       Print routing information from the FIB.  (This is the default.)

   -C
       Print routing information from the route cache.
[...]
```
We only want to know the meaning of the options `-t`, `-u`, `-l`, `-p`, `-e` and `-n`.
So we have to search in the entire documentation for each option.
Here this tool steps in:
For a given command line, this tool searchs each option in the man page and prints
the corresponding paragraph.
```
$ ./do.py netstat -tulpen
unknown param: -t

unknown param: -u

option: -l, --listening
descr:  Show only listening sockets.  (These are omitted by default.)

option: -p, --program
descr:  Show the PID and name of the program to which each socket belongs.

option: -e, --extend
descr:  Display additional information.  Use this option twice for maximum detail.

option: --numeric, -n
descr:  Show  numerical addresses instead of trying to determine symbolic host,
        port or user names.
```
The options `-t` and `-u` are not in a standard format and don't have a detailed
description, so these have to be searched manually if necessary. In the manpage they are (only) listed like this:
```
       netstat   {--statistics|-s}   [--tcp|-t]   [--udp|-u]   [--udplite|-U]   [--sctp|-S]
       [--raw|-w]
```


## Requirements

Unix with `man` and Python2.


## Usage

```
./do.py CLI
```

example:
```
$ ./do.py netstat -tulpen
unknown param: -t

unknown param: -u

option: -l, --listening
descr:  Show only listening sockets.  (These are omitted by default.)

option: -p, --program
descr:  Show the PID and name of the program to which each socket belongs.

option: -e, --extend
descr:  Display additional information.  Use this option twice for maximum detail.

option: --numeric, -n
descr:  Show  numerical addresses instead of trying to determine symbolic host,
        port or user names.
```

```
$ ./do.py curl -i http://github.com
option: -i, --include
descr:  Include  the  HTTP-header in the output. The HTTP-header includes things like
        server-name, date of the document, HTTP-version and more...
        See also -v, --verbose.
```


## TODO

- git plugin
