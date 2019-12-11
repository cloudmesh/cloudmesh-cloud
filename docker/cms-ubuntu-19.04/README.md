# Single Container with CMS and Mongo


The code in this directory wil create a single container that runs
mongo and cloudmesh.

The container is intended to explore how to create containers and use
an interactive shell in the container. It also shows you how to mount
your file system.

This container is not intended to be run in a production environment
yet.

Please let us know improvements that you see in this setup and we
integrate them.

We assume you have make installed on your system. If not, you can
execute the commands on your command line. If you run windows it is
easy to derive a appropriate `.bat` scripts (`make-shell.bat` and
`make-image.bat`). If you did, send it to us so we can distribute it
here.

## Checking out the code

To use this you need to check out the code with cloudmesh-installer

    $ mkdir cm
    $ cd cm
    $ pip install cloudmesh-installer -U
    $ cloudmesh-installer git clone cloud

Next go to the docker directory

    $ cd cloudmesh-cloud/cms-ubuntu19.04

## Creation of the image

The image can be created with 

    $ make image
    
To entre the interactive shell in the container use

    $ mkdir ~/.cloudmesh
    $ make shell
    
The shell assumes access to your `~/.cloudmesh` and `~/.ssh` directories.
Make sure to have both directories before you start make shell. Make
sure in your `.ssh` directory you have a `id_rsa` public and private key.

## Using cms in the container

As mentioned we assume you have configured your key in `.ssh`. If you do
not have a `cloudmesh.yaml` file you must create a directory before
calling make shell.

You can start cloudmesh just as described in the `cloudmesh-manual`:

* <https://cloudmesh.github.io/cloudmesh-manual/>

If you do not yet have a `cloudmesh.yaml` file you can create one
with

    # cms init
    
Now you can on your host system modify the ~/.cloudmesh/cloudmesh.yaml file.
After that you can now use cloudmesh. Test a couple of commands.

    # cms help
    # cms key add
    # cms key list
    
To get information from a cloud lets try chameleon (assuming you have
an account)

    # cms set cloud=chameleon
    # cms image list --refresh


## Bugs

If you have issues, please submit the to use via piazza or GitHub
issues, Make sure you do not submit passwords or other secrets. Do not
submit screenshots instead paste and copy the ASCII text from the
terminal. We will delete  all questions including screenshots instead of
ascii text and not read them.
