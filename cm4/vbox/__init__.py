from cloudmesh.common.Shell import Shell


def version(verbose=False):
    result = Shell.execute("vagrant", ["version"])
    if verbose:
        return result
    else:
        lines = result.split("\n")
        for line in lines:
            if "Installed Version:" in line:
                return line.replace("Installed Version:", "").strip()
        return None