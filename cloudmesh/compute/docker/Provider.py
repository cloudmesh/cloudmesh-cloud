import os
import shlex
import subprocess
import sys
import textwrap
from pprint import pprint

import docker
from docker.version import version as pydocker_version

from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
# from cloudmesh.abstractclass import ComputeNodeManagerABC
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.util import path_expand
from cloudmesh.terminal.Terminal import VERBOSE
from datetime import datetime

"""
is vagrant up to date

==> vagrant: A new version of Vagrant is available: 2.2.4 (installed version: 2.2.2)!
==> vagrant: To upgrade visit: https://www.vagrantup.com/downloads.html
"""


class Provider(ComputeNodeABC):

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
        if "cm" not in entry:
            entry["cm"] = {}
        entry["cm"]["kind"] = kind
        entry["cm"]["driver"] = self.cloudtype
        entry["cm"]["cloud"] = self.cloud
        entry["cm"]["name"] = entry["Name"]

        if kind == 'node':
            entry["cm"]["updated"] = str(datetime.utcnow())
            #entry["cm"]["name"] = entry["name"]

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
                      "state",
                      "image",
                      "public_ips",
                      "private_ips",
                      "cm.kind"],
            "header": ["name",
                       "cloud",
                       "state",
                       "image",
                       "public_ips",
                       "private_ips",
                       "kind"]
        },
        "image": {"sort_keys": ["Os"],
                  "order": ["RepoTags"
                            "repo",
                            "tags"
                            "Os",
                            "Size",
                            "Architecture"],
                  "header": ["RepoTags",
                             "repo",
                             "tags"
                             "Os",
                             "Size",
                             "Architecture"]},
        "flavor": {"sort_keys": ["name",
                                 "vcpus",
                                 "disk"],
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
                 configuration="~/.cloudmesh/.cloudmesh4.yaml"):
        VERBOSE.print(f"Init Docker {name}", verbose=9)
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

    def images(self):
        client = docker.from_env()
        images = client.images.list()
        pprint(images)
        result = []
        for image in images:
            image = dict(image.__dict__)['attrs']
            # image["repo"],image["tags"] = image["RepoTags"][0].split(":")
            image["repo"] = None
            image["tags"] = None
            image = self.update_dict(image, self.cloudtype)
            result.append(image)

        pprint(result)
        return result

    def delete_image(self, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                command = f"vagrant box remove {name}"
                result = Shell.execute(command, shell=True)
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
                command = f"vagrant box add {name} --provider virtualbox"
                result = Shell.live(command)
                assert result.status == 0
            except Exception as e:
                print(e)
                print(result)
                print()

            return result

    def _check_version(self, r):
        """
        checks if vargarnt version is up to date

        :return:
        """
        return "A new version of Vagrant is available" not in r

    def start(self, name, version, directory):
        """
        start a node

        :param version:
        :param directory:
        :param name: the unique node name
        :return:  The dict representing the node
        """
        command = f"docker run -v {directory}:/share -w /share --rm -it {name}:{version}  /bin/bash"
        os.system(command)

    def create(self, **kwargs):

        return None

    def execute(self, name, command, cwd=None):
        return None

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

        return None

    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        # TODO: find last name if name is None
        return None

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        # TODO: find last name if name is None
        return None

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        return None

    # @classmethod
    def delete(self, name=None):
        # TODO: check

        return None

    def dockerfile(self,
                   name=None,
                   directroy="~/.cloudmesh/docker/",
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
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """

        #
        # TODO BUG: if name contains not just letters and numbers and - return error, e. undersore not allowed
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

    def list(self, raw=True):
        """
        list all nodes id
    
        :return: an array of dicts representing the nodes
        """
        client = docker.from_env()
        containers = client.containers.list()
        pprint(containers)
        result = []
        for container in containers:
            container = dict(container.__dict__)['attrs']
            # image["repo"],image["tags"] = image["RepoTags"][0].split(":")
            container["repo"] = None
            container["tags"] = None
            container = self.update_dict(container, "node")
            result.append(container)

        pprint(result)
        return result

    def rename(self, name=None, destination=None):
        """
        rename a node
    
        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        return None
