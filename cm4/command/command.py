"""Vagrant Manager.

Usage:
  cm4 vagrant create --count <vm_number> [--debug]
  cm4 vagrant start [--vms=<vmList>] [--debug]
  cm4 vagrant stop [--vms=<vmList>] [--debug]
  cm4 vagrant destroy [--vms=<vmList>] [--debug]
  cm4 vagrant status [--vms=<vmList>]
  cm4 vagrant list
  cm4 vagrant ssh NAME
  cm4 vagrant run COMMAND  [--vms=<vmList>]
  cm4 vagrant script run SCRIPT [--vms=<vmList>]
  cm4 data add FILE
  cm4 data add SERVICE FILE
  cm4 data get FILE
  cm4 data get FILE DEST_FOLDER
  cm4 data del FILE
  cm4 data (ls | dir)
  cm4 set cloud=CLOUD
  cm4 set group=GROUP
  cm4 set role=ROLE
  cm4 set experiment=EXPERIMENT
  cm4 vm create --count <vm_number> [--debug]
  cm4 vm start [--vms=<vmList>] [--debug]
  cm4 vm stop [--vms=<vmList>] [--debug]
  cm4 vm destroy [--vms=<vmList>] [--debug]
  cm4 vm status [--vms=<vmList>]
  cm4 vm list
  cm4 vm ssh NAME
  cm4 vm run COMMAND  [--vms=<vmList>]
  cm4 vm script run SCRIPT [--vms=<vmList>]

  cm4 (-h | --help)
  cm4 --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --config      Location of a cmdata.yaml file


  cm4 -h

Options:
  -h --help     Show this screen.
  --vm_list=<list_of_vms>  List of VMs separated by commas ex: node-1,node-2

Description:
   put a description here

Example:
   put an example here
"""
from docopt import docopt
import cm4.vagrant.vagrant
import cm4.data.data
import cm4


def main():
    """
    Main function for the Vagrant Manager. Processes the input arguments.
    """
    version = cm4.__version__
    arguments = docopt(__doc__, version=version)
    cm4.vagrant.vagrant.process_arguments(arguments)
    cm4.data.vagrant.process_arguments(arguments)


if __name__ == "__main__":
    main()
