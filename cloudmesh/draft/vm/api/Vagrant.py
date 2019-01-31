import os
import re

from cloudmesh.abstractclass import ComputeNodeManagerABC


def execute(cmd, data, local=True):
    if local:
        print("run it locally")  # subprocess
    else:
        command = "ssh {username}@{hostname} \"{cmd}\"".format(**data, cmd=cmd)
        execute(command, data, local=True)


class Vagrant(ComputeNodeManagerABC):
    """
    Vagrant Manager.
    Provides the capabilities to manage a Vagrant Cluster of nodes via the script.
    """

    def __init__(self, debug=False):
        """
        TODO: doc

        :param debug:
        """
        # prepare path
        #
        # TODO: BUG: We use cloudmesh, ehvagrant is not whow we set this up
        #
        # THis should use a config = Config()
        #

        self.workspace = os.path.join(os.path.expanduser('~'), '.cloudmesh', 'vagrant_workspace', )
        self.path = os.path.join(self.workspace, "Vagrantfile")
        self.experiment_path = os.path.join(self.workspace, 'experiment')

        # prepare folder and Vagrantfile
        #
        #  TODO: BUG: Thsi should be a utility function in common
        #
        if not os.path.isdir(self.workspace):
            self._nested_mkdir(self.workspace)

        if not os.path.isdir(self.experiment_path):
            os.mkdir(self.experiment_path)

        #
        # TODO: BUG: I do not understand what node 1 and node2 are, seems debugging code
        #
        if not os.path.isfile(self.path):
            self.create(['node1', 'node2'])

        self.ssh_config = {}
        self.debug = debug

    def ssh(self, name):
        """
        TODO: doc

        :param name:
        :return:
        """
        self.execute("vbox ssh " + str(name))

    def create(self, hosts, image='ubuntu/xenial64', output_path=None, template=None):
        """
        TODO: doc

        :return:
        """
        # prepare dict
        kwargs = {}
        array = ["'{}'".format(x) for x in hosts]
        kwargs.update({'array': ','.join(array)})
        kwargs.update({'image': image})

        # prepare template
        if not template:
            template = """
            Vagrant.configure("2") do |config|    
              ([{array}]).each do |name|
                config.vm.define "#{{name}}" do |node|
                  node.vm.box = "{image}"
                end
              end
            end
            """

        # write
        if not output_path:
            output_path = self.path
        with open(output_path, 'w') as out:
            out.write(template.format(**kwargs))

    def start(self, name=None):
        """
        Default: Starts all the VMs specified.
        If @name is provided, only the named VM is started.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vbox up " + str(name))

    def resume(self, name=None):
        """
        Default: resume(start) all the VMs specified.
        If @name is provided, only the named VM is started.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """

        if name is None:
            # start all
            name = ""
        self.execute("vbox up " + str(name))

    def stop(self, name=None):
        """
        Default: Stops all the VMs specified.
        If @name is provided, only the named VM is stopped.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vbox halt " + str(name))

    def suspend(self, name=None):
        """
        TODO: doc

        :param name:
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vbox suspend " + str(name))

    def destroy(self, name=None, force=False):
        """
        Default: Destroys all the VMs specified.
        If @name is provided, only the named VM is destroyed.

        :param force:
        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            name = ""
        self.execute("vbox destroy {}{}".format('-f ' if force else '', name))

    def ls(self, name=None):
        """
        Provides the status information of all Vagrant Virtual machines by default.
        If a name is specified, it provides the status of that particular virtual machine.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vbox status " + str(name))

    def info(self, name):
        """
        provides the status of that particular virtual machine.

        :return:
        """
        self.execute("vbox status " + name)

    def download(self, name, source, dest, prefix_dest=False, recursive=False):
        """
        TODO: doc

        :return:
        """
        if prefix_dest:
            if os.path.isdir(dest):
                dest = os.path.join(dest, name)
                if not os.path.isdir(dest):
                    os.mkdir(dest)
            else:
                path_split = re.split('[\\\\/]', dest)
                if path_split[-1]:
                    path_split.insert(-1, name)
                    path_split = self._impute_drive_sep(path_split)
                    dest = os.path.join(*path_split)

        r = (not os.path.basename(source) or recursive)
        self._scp(name, 'download', source, dest, r)

    def upload(self, name, source, dest, recursive=False):
        """
        TODO: doc

        :return:
        """
        r = (not os.path.basename(source) or recursive)
        self._scp(name, 'upload', source, dest, r)
