# VM Providers

Cm4 works straight forward with a number of providers under the assumption you have accounts on these frameworks. We demonstrate hete how to start a singel vm on each of these providers and list the started vms. Defaults form the configuration file are used to select images and flavors. These defaults can naturally be changed.

## General Interface

```bash
$ cm4 set cloud=<cloudname as defined in the ~/.cloudmesh/cloudmesh4.yaml>
$ cm4 vm start
$ cm4 vm list

$ cm4 flavor="medium"
$ cm4 image="ubuntu18.04"

$ cm4 vm start
```

## Explicit Use with Options

```bash
$ cm4 vm start --cloud=chameleon --image=ubuntu18.04 --flavor=medium --key=~/.ssh/id_rsa.bub
```




## Vagrant

TODO

```bash
$ cm4 set cloud=vagrant
$ cm4 vm start
$ cm4 vm list
```

## AWS

```bash
$ cm4 set cloud=aws
$ cm4 vm start
$ cm4 vm list
```

## Azure

```bash
$ cm4 set cloud=azure
$ cm4 vm start
$ cm4 vm list
```

## OpenStack


### Jetstream

TODO

```bash
$ cm4 set cloud=jetstream
$ cm4 vm start
$ cm4 vm list
```

### Chameleon Cloud

```bash
$ cm4 set cloud=chameleon
$ cm4 vm start
$ cm4 vm list
```

### Cybera

TODO

```bash
$ cm4 set cloud=cybera
$ cm4 vm start
$ cm4 vm list
```


### DevStack

TODO

```bash
$ cm4 set cloud=devstack
$ cm4 vm start
$ cm4 vm list
```
