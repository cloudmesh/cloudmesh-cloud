import os
import shlex
import subprocess
import sys
import textwrap
from datetime import datetime
from pprint import pprint

import docker
from cloudmesh.abstract.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand
# from cloudmesh.abstract import ComputeNodeManagerABC
from cloudmesh.configuration.Config import Config
from docker.version import version as pydocker_version

"""
is vagrant up to date

==> vagrant: A new version of Vagrant is available: 2.2.4 (installed version: 2.2.2)!
==> vagrant: To upgrade visit: https://www.vagrantup.com/downloads.html
"""


class Provider(ComputeNodeABC):
    kind = "docker"

    def run_command(self, command):
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.read(1)
            if output == b'' and process.poll() is not None:
                break
            if output:
                sys.stdout.write(output.decode("utf-8"))
                sys.stdout.flush()
        rc = process.poll()
        return rc

    def update_dict(self, entry, kind="node"):
        """
        updates the dict with

          "cm": {
             "kind": ...,
             "name": ...,
             "cloud": ...,
             "driver" ...,
             }
        :param entry: the entry
        :type entry: dict
        :param kind: a string representing the kind
        :type kind: string
        :return: the modified entry
        :rtype: dict
        """
        if "cm" not in entry:
            entry["cm"] = {}
        entry["cm"]["kind"] = kind
        entry["cm"]["driver"] = self.cloudtype
        entry["cm"]["cloud"] = self.cloud
        if kind == "image":
            if "RepoTags" in entry:
                entry["cm"]["name"] = entry["RepoTags"][0]

        if kind == 'node':

            entry["cm"]["updated"] = str(datetime.utcnow())
            entry["cm"]["name"] = entry["Name"]

            if "Created_at" in entry:
                entry["cm"]["created"] = str(entry["Created"])
            if entry["State"]["StartedAt"]:
                entry["cm"]["started"] = entry["State"]["StartedAt"]
        return entry

    output = {

        "vm": {
            "sort_keys": ["cm.name"],
            "order": ["cm.name",
                      "cm.cloud",
                      "State.Status",
                      "Config.Image",
                      "NetworkSettings.IPAddress",
                      "cm.kind"],
            "header": ["cm.name",
                       "cm.cloud",
                       "Status",
                       "image",
                       "public_ips",
                       "kind"]
        },
        "image": {
            "sort_keys": ["cm.name"],
            "order": ["RepoTags",
                      "repo",
                      "tags",
                      "Os",
                      "Size",
                      "Architecture"],
            "header": ["RepoTags",
                       "repo",
                       "tags",
                       "Os",
                       "Size",
                       "Architecture"]},
        "flavor": {"sort_keys": ["cm.name"],
                   "order": ["name",
                             "vcpus",
                             "ram",
                             "disk"],
                   "header": ["Name",
                              "VCPUS",
                              "RAM",
                              "Disk"]}

    }

    def __init__(self, name=None,
                 configuration="~/.cloudmesh/.cloudmesh.yaml"):
        VERBOSE(f"Init Docker {name}")
        self.config = Config()
        conf = Config(configuration)["cloudmesh"]
        self.user = conf["profile"]
        self.spec = conf["cloud"][name]
        self.cloud = name
        cred = self.spec["credentials"]
        self.cloudtype = self.spec["cm"]["kind"]

        # m = MongoDBController()
        # status = m.status()
        # if status.status == "error":
        #    raise Exception("ERROR: MongoDB is not running.")
        #
        # BUG: Naturally the following is wrong as it depends on the name.
        #
        # super().__init__("vagrant", config)

    def version(self):
        """
        This command returns the versions ov vagrant and virtual box
        :return: A dict with the information

        Description:

          The output looks like this

        """

        def get_version(command):
            data = dotdict()
            version, build = Shell.execute("docker --version",
                                           shell=True).split(",")
            build = build.split("build ")[1]
            version = version.split("version ")[1]
            data.version = version
            data.command = command
            data.build = build
            return data

        versions = dotdict({
            "pydocker": dotdict({"version": pydocker_version}),
            "docker": get_version("docker"),
            "machine": get_version("docker-machine"),
            "compose": get_version("docker-compose")
        })

        return versions

    def list(self, raw=True):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """

        print("x")
        client = docker.from_env()
        containers = client.containers.list()

        result = []
        for container in containers:
            container = dict(container.__dict__)['attrs']
            container["repo"] = None
            container["tags"] = None
            container = self.update_dict(container, "node")
            result.append(container)

        return result

    def images(self):
        client = docker.from_env()
        images = client.images.list()
        result = []
        for image in images:
            image = dict(image.__dict__)['attrs']
            # image["repo"],image["tags"] = image["RepoTags"][0].split(":")
            image["repo"] = None
            image["tags"] = None
            image = self.update_dict(image, "image")
            result.append(image)
        return result

    def delete_image(self, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                raise NotImplementedError
            except Exception as e:
                print(e)

            return result

    def add_image(self, name=None):

        command = f"vagrant box add {name} --provider virtualbox"

        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                raise NotImplementedError
            except Exception as e:
                print(e)
                print(result)
                print()

            return result

    def _check_version(self, r):
        """
        checks if vagrant version is up to date

        :return:
        """
        raise NotImplementedError

    def start(self, name, version, directory):
        """
        start a node

        :param version:
        :param directory:
        :param name: the unique node name
        :return:  The dict representing the node
        """
        command = f"docker run -v {directory}:/share -w /share --rm " \
                  f"-it {name}:{version}  /bin/bash"
        os.system(command)

    def create(self, **kwargs):
        raise NotImplementedError

        return None

    def execute(self, name, command, cwd=None):
        return None

    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        raise NotImplementedError

        pass

    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """
        raise NotImplementedError

        return None

    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        # TODO: find last name if name is None
        raise NotImplementedError

        return None

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        # TODO: find last name if name is None
        raise NotImplementedError

        return None

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        raise NotImplementedError

        return None

    # @classmethod
    def delete(self, name=None):
        # TODO: check
        raise NotImplementedError

        return None

    def dockerfile(self,
                   name=None,
                   directory="~/.cloudmesh/docker/",
                   os="ubuntu",
                   version="18.04",
                   **kwargs):

        if name is None:
            Console.error("name is not specified")
            sys.exit(1)

        arg = (self.local())
        arg.update(kwargs)

        script = {"ubuntu": textwrap.dedent("""
            #
            # cloudmesh dockerfile
            #
            FROM {os}:{version}
            
            # update the OS
            RUN apt-get update
            
            #Define the ENV variable
            #ENV TMP /tmp
 
            # COPY
            #COPY default backup
 
            #RUN mkdir ~/.cloudmesh
 
            # Volume configuration
            #VOLUME ["sample"]
 
            # Configure Services and Port
            #CMD ["cms"]
            
            EXPOSE 80 443
            
           """.format(**arg))}

        return script

    def _get_specification(self,
                           cloud=None,
                           name=None,
                           port=None,
                           image=None, **kwargs):
        arg = dotdict(kwargs)
        arg.port = port
        config = Config()
        pprint(self.config)

        if cloud is None:
            #
            # TOD read default cloud
            #
            cloud = "vagrant"  # TODO must come through parameter or set cloud

        spec = config.data["cloudmesh"]["cloud"][cloud]
        default = spec["default"]
        pprint(default)

        if name is not None:
            arg.name = name
        else:
            # TODO get new name
            pass

        if image is not None:
            arg.image = image
        else:
            arg.image = default["image"]
            pass

        arg.path = default["path"]
        arg.directory = path_expand("{path}/{name}".format(**arg))
        arg.vagrantfile = "{directory}/Dockerfile".format(**arg)
        return arg

    def create_spec(self, name=None, image=None, size=1024, timeout=360,
                    port=80,
                    **kwargs):
        """
        creates a named node

        :param port:
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the
                        image does not boot. The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """

        #
        # TODO BUG: if name contains not just letters and numbers and -
        #  return error, e. underscore not allowed
        #

        arg = self._get_specification(name=name,
                                      image=image,
                                      size=size,
                                      memory=size,
                                      timeout=timeout,
                                      port=port,
                                      **kwargs)

        if not os.path.exists(arg.directory):
            os.makedirs(arg.directory)

        configuration = self.vagrantfile(**arg)

        with open(arg.vagrantfile, 'w') as f:
            f.write(configuration)

        pprint(arg)

        return arg

    def rename(self, source=None, destination=None):
        """
        rename a node
    
        :param destination:
        :param source: the current name
        :return: the dict with the new name
        """
        result = None
        client = docker.from_env()
        containers = client.containers.list()

        for container in containers:
            pprint(container)
            pprint(container.__dict__['attrs'])
            entry = container.__dict__['attrs']
            # if container["cm"]["name"] == source:
            if entry["Name"] == source:
                container.rename(destination)
                result = dict(container.__dict__)['attrs']
                result = self.update_dict(result, "node")
                break

        return result

    def flavors(self):
        Console.error("flavors not implemented")
        return None

    def keys(self):
        Console.error("keys not implemented")
        return None

    def key_upload(self, key):
        Console.error("keys upload implemented")
        return None
