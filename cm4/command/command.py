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
  cm4 set host=HOSTNAME
  cm4 set cluster=CLUSTERNAME
  cm4 set experiment=EXPERIMENT
  cm4 vm create --count <vm_number> [--debug] [--dryrun]
  cm4 vm start [--vms=<vmList>] [--debug] [--dryrun]
  cm4 vm stop [--vms=<vmList>] [--debug] [--dryrun]
  cm4 vm destroy [--vms=<vmList>] [--debug] [--dryrun]
  cm4 vm status [--vms=<vmList>] [--dryrun]
  cm4 vm list
  cm4 vm ssh NAME
  cm4 vm run COMMAND  [--vms=<vmList>]
  cm4 vm script run SCRIPT [--vms=<vmList>] [--dryrun]
  cm4 vcluster create virtual-cluster <virtualcluster-name> --clusters=<clusterList> [--computers=<computerList>] [--debug]
  cm4 vcluster destroy virtual-cluster <virtualcluster-name>
  cm4 vcluster create runtime-config <config-name> <proc-num> in:params out:stdout [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config <config-name> <proc-num> in:params out:file [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config <config-name> <proc-num> in:params+file out:stdout [--download-proc-num=<download-pnum> [default=1]]  [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config <config-name> <proc-num> in:params+file out:file [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config <config-name> <proc-num> in:params+file out:stdout+file [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster set-param runtime-config <config-name> <parameter> <value>
  cm4 vcluster destroy runtime-config <config-name>
  cm4 vcluster list virtual-clusters [<depth> [default:1]]
  cm4 vcluster list runtime-configs [<depth> [default:1]]
  cm4 vcluster run-script <job-name> <virtualcluster-name> <config-name> <script-path> <set-of-params-list> <remote-path> <save-to> [--argfile-path=<argfile-path>] [--outfile-name=<outfile-name>] [--suffix=<suffix>] [--overwrite]
  cm4 vcluster fetch <job-name>
  cm4 vcluster clean-remote <job-name> <proc-num>
  cm4 vcluster test-connection <virtualcluster-name> <proc-num>
  cm4 spark deploy -n 10 [--dryrun]
  cm4 spark run [--dryrun]
  cm4 spark execute PRG [--dryrun]
  cm4 (-h | --help)
  cm4 --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --config      Location of a cmdata.yaml file
  --vm_list=<list_of_vms>  List of VMs separated by commas ex: node-1,node-2

Description:
   put a description here

Example:
   put an example here
"""
from docopt import docopt
import cm4.vagrant.vagrant
import cm4.vcluster.VirtualCluster
import cm4.data.data
import cm4


def main():
    """
    Main function for the Vagrant Manager. Processes the input arguments.
    """
    version = cm4.__version__
    arguments = docopt(__doc__, version=version)
    cm4.vagrant.vagrant.process_arguments(arguments)
    cm4.vcluster.VirtualCluster.process_arguments(arguments)
    # cm4.data.vagrant.process_arguments(arguments)  # this call is raising this error: module 'cm4.data' has no attribute 'vagrant'


if __name__ == "__main__":
    main()
