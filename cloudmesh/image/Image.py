class Image(object):

    @staticmethod
    def guess_username(image, cloud=None):
        """
        guess the default user name based on the VM name and cloud

        :param image: the name of the image
        :param cloud: the name of the cloud
        :return: the proposed username
        """
        username = "root"

        image = image.lower()
        if image.startswith("cc-") or cloud == 'chameleon':
            username = "cc"
        elif any(x in image for x in ["ubuntu", "wily", "xenial"]):
            username = "ubuntu"
        elif image.startswith("oracle"):
            username = "opc"
        elif "centos" in image:
            username = "root"
        elif "fedora" in image:
            username = "root"
        elif "rhel" in image:
            username = "root"
        elif "cirros" in image:
            username = "root"
        elif "coreos" in image:
            username = "root"
        else:
            username = "root"
        return username
