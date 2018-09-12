"""Vagrant Manager.

Usage:
  vagrant.py vagrant create --vms <vm_number>
  vagrant.py vagrant start [--vm_list=<vmList>]
  vagrant.py vagrant stop [--vm_list=<vmList>]
  vagrant.py vagrant destroy [--vm_list=<vmList>]
  vagrant.py vagrant status [--vm_list=<vmList>]
  vagrant.py -h

Options:
  -h --help     Show this screen.
  --vm_list=<list_of_vms>  List of VMs separated by commas ex: node-1,node-2
  
Description:
   put a description here
   
Example:
   put an example here
"""
from __future__ import print_function
import fileinput
import re
import subprocess
import os
from docopt import docopt


class Vagrant(object):

    def __init__(self):
        self.workspace = "./vagrant_workspace"

    def execute(self, command):
        subprocess.run(command,
                       cwd=self.workspace,
                       check=True,
                       shell=True)

    def status_all_vms(self):
        self.execute("vagrant status")

    def status_vm(self, name):
        self.execute("vagrant status " + str(name))

    def start_all_vms(self):
        self.execute("vagrant up")

    def start_vm(self, name):
        self.execute("vagrant up " + str(name))

    def stop_all_vms(self):
        self.execute("vagrant halt")

    def stop_vm(self, name):
        self.execute("vagrant halt " + str(name))

    def destroy_all_vms(self):
        self.execute("vagrant destroy")

    def destroy_vm(self, name):
        self.execute("vagrant destroy " + str(name))

    def generate_vagrantfile(self, number_of_nodes):
        replacement_string = "NUMBER_OF_NODES = " + str(number_of_nodes)
        for line in fileinput.FileInput(os.path.join(self.workspace, "Vagrantfile"), inplace=True):
            line = re.sub("NUMBER_OF_NODES.*(\d+)$", replacement_string, line.rstrip())
            print(line)


def process_arguments(arguments):
    if arguments.get("vagrant"):
        provider = Vagrant()
        if arguments.get("create") & arguments.get("--vms"):
            provider.generate_vagrantfile(arguments.get("<vm_number>"))
        elif arguments.get("start"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    provider.start_vm(node_name)
            else:
                provider.start_all_vms()
        elif arguments.get("stop"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    provider.stop_vm(node_name)
            else:
                provider.stop_all_vms()
        elif arguments.get("destroy"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    provider.destroy_vm(node_name)
            else:
                provider.destroy_all_vms()
        elif arguments.get("status"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    provider.status_vm(node_name)
            else:
                provider.status_all_vms()


def main():
    arguments = docopt(__doc__, version='Vagrant Manager 1.0')
    process_arguments(arguments)


if __name__ == "__main__":
    main()
