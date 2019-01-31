version
=======

::

  Usage:
    version pip [PACKAGE]
    version [--format=FORMAT] [--check=CHECK]


  Options:
    --format=FORMAT  the format to print the versions in [default: table]
    --check=CHECK    boolean tp conduct an additional check [default: True]

  Description:
    version 
        Prints out the version number
    version pip
        Prints the contents of pip list

  Limitations:
    Package names must not have a . in them instead you need to use -
    Thus to query for cloudmesh.cmd5 use

      cms version pip cloudmesh-cmd5

