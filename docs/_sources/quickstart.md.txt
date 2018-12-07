# Quickstart

## Commandline

```bash
$ cm4 set cloud=vagrant
$ cm4 vm start
$ cm4 image list
$ cm4 flavor list

$ cm4 set cloud=aws
$ cm4 vm start
$ cm4 image list
$ cm4 flavor list

$ cm4 set cloud=azure
$ cm4 vm start
$ cm4 image list
$ cm4 flavor list

$ cm4 set cloud=chameleon
$ cm4 vm start
$ cm4 image list
$ cm4 flavor list

$ cm4 set cloud=jetstream
$ cm4 vm start
$ cm4 image list
$ cm4 flavor list

$ cm4 vm list
```

## Interactive shell

BUG: Feature not yet implemented.

As we want to often start or interact with a lot of virtual machines, it may be easier to run cm4 as an interactive shell.  Here is a simple example that starts cm4 and simply executes the sommands within the cm4 command shell.

```bash
cm4
cm4> set cloud=aws
cm4> vm start
```



