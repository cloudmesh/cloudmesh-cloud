# Vagrant

This has to be reimplemented for Python 3

```bash
cm4 set cloud=vagrant
```

See <https://github.com/cloudmesh/vagrant>


```
Usage:
  cm4 vbox version [--format=FORMAT]
  cm4 vbox image list [--format=FORMAT]
  cm4 vbox image find NAME
  cm4 vbox image add NAME
  cm4 vbox vm list [--format=FORMAT] [-v]
  cm4 vbox vm delete NAME
  cm4 vbox vm config NAME
  cm4 vbox vm ip NAME [--all]
  cm4 vbox create NAME ([--memory=MEMORY]
                       [--image=IMAGE]
                       [--script=SCRIPT] | list)
  cm4 vbox vm boot NAME ([--memory=MEMORY]
                        [--image=IMAGE]
                        [--port=PORT]
                        [--script=SCRIPT] | list)
  cm4 vbox vm ssh NAME [-e COMMAND]
```

For each named vbox a directory is created in whcih a Vagrant file is placed that than is used to interact with the virtual box
The location of teh directory is ~/.cloudmesh/vagrant/NAME.


If you set however the cloud to vbox you can save yourself the vbox command in consecutive calls and just use


```
Usage:
  cm4 version [--format=FORMAT]
  cm4 image list [--format=FORMAT]
  cm4 image find NAME
  cm4 image add NAME
  cm4 vm list [--format=FORMAT] [-v]
  cm4 vm delete NAME
  cm4 vm config NAME
  cm4 vm ip NAME [--all]
  cm4 create NAME ([--memory=MEMORY]
                       [--image=IMAGE]
                       [--script=SCRIPT] | list)
  cm4 vm boot NAME ([--memory=MEMORY]
                        [--image=IMAGE]
                        [--port=PORT]
                        [--script=SCRIPT] | list)
  cm4 vm ssh NAME [-e COMMAND]
```
