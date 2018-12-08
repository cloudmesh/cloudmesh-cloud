from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from cloudmesh.common.Shell import Shell
import webbrowser
from cloudmesh.common.dotdict import dotdict
import os

class VboxProvider (CloudManagerABC):

    #
    # if name is none, take last name from mongo, apply to last started vm
    #

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

        :param name: the current name
        :param new_name: the new name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        pass

    #
    # Additional methods
    #


    @classmethod
    def find_image(cls, keywords):
        """
        Finds an image on hashicorps web site

        :param keywords: The keywords to narrow down the search
        """
        d = {
            'key': '+'.join(keywords),
            'location': "https://app.vagrantup.com/boxes/search"
        }
        link = "{location}?utf8=%E2%9C%93&sort=downloads&provider=&q=\"{key}\"".format(**d)
        webbrowser.open(link, new=2, autoraise=True)

    @classmethod
    def add_image(cls, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "add", name])
                os.system("vagrant box add {name}".format(name=name))
            except Exception as e:
                print(e)

            return result

    @classmethod
    def delete_image(cls, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "remove", name])
                os.system("vagrant box remove {name}".format(name=name))
            except Exception as e:
                print(e)

            return result
    @classmethod
    def list_images(cls):
        def convert(line):
            line = line.replace("(", "")
            line = line.replace(")", "")
            line = line.replace(",", "")
            entry = line.split(" ")
            data = dotdict()
            data.name = entry[0]
            data.provider = entry[1]
            data.date = entry[2]
            return data

        result = Shell.execute("vagrant", ["box", "list"])

        if "There are no installed boxes" in result:
            return None
        else:
            result = result.split("\n")
        lines = []
        for line in result:
            lines.append(convert(line))

        return lines