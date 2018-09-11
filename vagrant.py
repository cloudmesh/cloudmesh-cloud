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
"""

import fileinput
import re
import subprocess
from docopt import docopt


def main():
    arguments = docopt(__doc__, version='Vagrant Manager 1.0')
    process_arguments(arguments)


def process_arguments(arguments):
    if arguments.get("vagrant"):
        if arguments.get("create") & arguments.get("--vms"):
            generate_vagrant_file(arguments.get("<vm_number>"))
        elif arguments.get("start"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    start_vagrant_vm(node_name)
            else:
                start_all_vagrant_vms()
        elif arguments.get("stop"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    stop_vagrant_vm(node_name)
            else:
                stop_all_vagrant_vms()
        elif arguments.get("destroy"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    destroy_vagrant_vm(node_name)
            else:
                destroy_all_vagrant_vms()
        elif arguments.get("status"):
            if arguments.get("--vm_list"):
                for node_name in arguments.get("--vm_list").split(','):
                    status_vagrant_vm(node_name)
            else:
                status_all_vagrant_vms()


def status_all_vagrant_vms():
    subprocess.run("vagrant status", cwd="./vagrant_workspace", check=True, shell=True)


def status_vagrant_vm(vm_name):
    subprocess.run("vagrant status " + str(vm_name), cwd="./vagrant_workspace", check=True, shell=True)


def start_all_vagrant_vms():
    subprocess.run("vagrant up", cwd="./vagrant_workspace", check=True, shell=True)


def start_vagrant_vm(vm_name):
    subprocess.run("vagrant up " + str(vm_name), cwd="./vagrant_workspace", check=True, shell=True)


def stop_all_vagrant_vms():
    subprocess.run("vagrant halt", cwd="./vagrant_workspace", check=True, shell=True)


def stop_vagrant_vm(vm_name):
    subprocess.run("vagrant halt " + str(vm_name), cwd="./vagrant_workspace", check=True, shell=True)


def destroy_all_vagrant_vms():
    subprocess.run("vagrant destroy", cwd="./vagrant_workspace", check=True, shell=True)


def destroy_vagrant_vm(vm_name):
    subprocess.run("vagrant destroy " + str(vm_name), cwd="./vagrant_workspace", check=True, shell=True)


def generate_vagrant_file(number_of_nodes):
    replacement_string = "NUMBER_OF_NODES = " + str(number_of_nodes)
    for line in fileinput.FileInput("vagrant_workspace/Vagrantfile", inplace=True):
        line = re.sub("NUMBER_OF_NODES.*(\d+)$", replacement_string, line.rstrip())
        print(line)


if __name__ == "__main__":
    main()
