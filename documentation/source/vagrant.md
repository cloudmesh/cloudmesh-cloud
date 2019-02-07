# Vagrant (outdated)

This has to be reimplemented for Python 3

```bash
cm4 set cloud=vagrant
```

See <https://github.com/cloudmesh/vagrant>


```
Usage:
  cms vbox version [--format=FORMAT]
  cms vbox image list [--format=FORMAT]
  cms vbox image find NAME
  cms vbox image add NAME
  cms vbox vm list [--format=FORMAT] [-v]
  cms vbox vm delete NAME
  cms vbox vm config NAME
  cms vbox vm ip NAME [--all]
  cms vbox create NAME ([--memory=MEMORY]
                       [--image=IMAGE]
                       [--script=SCRIPT] | list)
  cms vbox vm boot NAME ([--memory=MEMORY]
                        [--image=IMAGE]
                        [--port=PORT]
                        [--script=SCRIPT] | list)
  cms vbox vm ssh NAME [-e COMMAND]
```

For each named vbox a directory is created in whcih a Vagrant file is placed that than is used to interact with the virtual box
The location of teh directory is ~/.cloudmesh/vagrant/NAME.


If you set however the cloud to vbox you can save yourself the vbox command in consecutive calls and just use


```
Usage:
  cms version [--format=FORMAT]
  cms image list [--format=FORMAT]
  cms image find NAME
  cms image add NAME
  cms vm list [--format=FORMAT] [-v]
  cms vm delete NAME
  cms vm config NAME
  cms vm ip NAME [--all]
  cms create NAME ([--memory=MEMORY]
                       [--image=IMAGE]
                       [--script=SCRIPT] | list)
  cms vm boot NAME ([--memory=MEMORY]
                        [--image=IMAGE]
                        [--port=PORT]
                        [--script=SCRIPT] | list)
  cms vm ssh NAME [-e COMMAND]
```
