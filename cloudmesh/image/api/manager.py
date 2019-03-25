class Manager(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))

    def list(self, parameter):
        print("list", parameter)

    @classmethod
    def guess_username(cls, name, cloud=None):
        """
        gues the default usernamed based on the VM name and cloud

        :param name: the name of the image
        :param cloud: the name of the cloud
        :return: the proposed username
        """
        name = name.lower()
        if name.startswith("cc-") or cloud=='chameleon':
            username = "cc"
        elif any(x in name for x in ["ubuntu", "wily", "xenial"]):
            username = "ubuntu"
        elif "centos" in name:
            username = "root"
        elif "fedora" in name:
            username = "root"
        elif "rhel" in name:
            username = "root"
        elif "cirros" in name:
            username = "root"
        elif "coreos" in name:
            username = "root"

        return username