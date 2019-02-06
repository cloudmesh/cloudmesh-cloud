flavor
======

::

    Usage:
        flavor refresh [--cloud=CLOUD] [-v]
        flavor list [ID] [--cloud=CLOUD] [--format=FORMAT] [--refresh] [-v]
        This lists out the flavors present for a cloud
    Options:
       --format=FORMAT  the output format [default: table]
       --cloud=CLOUD    the cloud name
       --refresh        refreshes the data before displaying it
                        from the cloud
    Examples:
        cm flavor refresh
        cm flavor list
        cm flavor list --format=csv
        cm flavor show 58c9552c-8d93-42c0-9dea-5f48d90a3188 --refresh

