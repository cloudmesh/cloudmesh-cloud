storage
=======

::

  Usage:
        starage [--storage=SERVICE] put FILENAME
        starage [--storage=SERVICE] get FILENAME
        starage [--storage=SERVICE] delete FILENAME
        starage [--storage=SERVICE] size FILENAME
        starage [--storage=SERVICE] info FILENAME
        storage [--storage=SERVICE] create FILENAME
        storage [--storage=SERVICE] sync SOURCEDIR DESTDIR


  This command does some useful things.

  Arguments:
      FILE   a file name


  Options:
      -f      specify the file

  Example:
    set storage=box
    starage  put FILENAME

    is the same as 

    starage  --storage=box put FILENAME

