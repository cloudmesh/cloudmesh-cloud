# Quickstart

## Commandline

```bash
$ cms set cloud=vagrant
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=aws
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=azure
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=chameleon
$ cms vm start
$ cms image list
$ cms flavor list

$ cms set cloud=jetstream
$ cms vm start
$ cms image list
$ cms flavor list

$ cms vm list
```

## Interactive shell

BUG: Feature not yet implemented.

As we want to often start or interact with a lot of virtual machines, it may be easier to run cm4 as an interactive shell.  Here is a simple example that starts cm4 and simply executes the sommands within the cm4 command shell.

```bash
cms
cms> set cloud=aws
cms> vm start
```



