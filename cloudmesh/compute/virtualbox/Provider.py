from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from pprint import pprint
from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict
from datetime import datetime
import os

class Provider(ComputeNodeABC):

    def __init__(self, name=None, configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        pass

    def images(self):
        def convert(data_line):
            data_line = data_line.replace("(", ",")
            data_line = data_line.replace(")", ",")
            data_entry = data_line.split(",")
            data = dotdict()
            data.name = data_entry[0].strip()
            data.provider = data_entry[1].strip()
            data.comment = data_entry[2].strip()
            return data

        result = Shell.execute("vagrant box list")

        pprint(result)

        if "There are no installed boxes" in result:
            return None
        else:
            result = result.split("\n")
        lines = []
        for line in result:
            entry = convert(line)
            if "date" in entry:
                date = entry["date"]
                # "20181203.0.1"
                #entry["date"] = datetime.strptime(date, '%Y%m%d.%H.%M')
            lines.append(entry)

        return lines

    def delete_image(self, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "remove", name])
                result = Shell.vagrant("box remove {name}".format(name))
            except Exception as e:
                print(e)

            return result

    def add_image(self, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "add", name])
                result = Shell.vagrant(["box", "add", name, "--provider",  "virtualbox"])
            except Exception as e:
                print(e)

            return result

    def start(self, name):
        """
        start a node
    
        :param name: the unique node name
        :return:  The dict representing the node
        """
        pass

    def stop(self, name=None):
        """
        stops the node with the given name
    
        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    def info(self, name=None):
        """
        gets the information of a node with a given name
    
        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    def suspend(self, name=None):
        """
        suspends the node with the given name
    
        :param name: the name of the node
        :return: The dict representing the node
        """
        pass

    def list(self):
        """
        list all nodes id
    
        :return: an array of dicts representing the nodes
        """
        pass

    def resume(self, name=None):
        """
        resume the named node
    
        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        """
        creates a named node
    
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """
        pass

    def rename(self, name=None, destination=None):
        """
        rename a node
    
        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        pass
