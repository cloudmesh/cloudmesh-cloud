from pprint import pprint

import psutil


def psutil_ps():
    found = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
        except psutil.NoSuchProcess:
            pass
        else:
            found.append(pinfo)
    if len(pinfo) == 0:
        return None
    else:
        return found

pprint(psutil_ps())
