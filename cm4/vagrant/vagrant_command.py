#
# Here we store the vagrant command which is separated from the provider
#
"""
Vagrant Manager.

Usage:
  cm4 vagrant create --vms=VMLIST [--box=BOX] [--template=TEMPLATE] [--output=OUTPUT] [--debug]
  cm4 vagrant start [--vms=VMLIST] [--debug]
  cm4 vagrant resume [--vms=VMLIST] [--debug]
  cm4 vagrant stop [--vms=VMLIST] [--debug]
  cm4 vagrant suspend [--vms=VMLIST] [--debug]
  cm4 vagrant destroy [-f] [--vms=VMLIST] [--debug] 
  cm4 vagrant info NAME [--debug]
  cm4 vagrant ls [--debug]
  cm4 vagrant upload --from=FROM --to=TO [-r] [--vms=VMLIST] [--debug]
  cm4 vagrant download --from=FROM --to=TO [-r] [--vms=VMLIST] [--debug]
  cm4 vagrant ssh NAME [--debug]
  cm4 vagrant run command COMMAND [--vms=VMLIST] [--debug]
  cm4 vagrant run script SCRIPT [--data=PATH] [--vms=VMLIST] [--debug]

  cm4 -h

Options:
  -h --help     Show this screen.
  --vm_list=<list_of_vms>  List of VMs separated by commas ex: node-1,node-2

Description:
   put a description here
   
Example:
   put an example here
"""