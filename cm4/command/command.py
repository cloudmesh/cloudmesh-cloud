"""Cloudmesh 4

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
  cm4 set cloud CLOUD
  cm4 set group GROUP
  cm4 set role ROLE
  cm4 set host HOSTNAME
  cm4 set cluster CLUSTERNAME
  cm4 set experiment EXPERIMENT
  cm4 set --key=KEY --value=VALUE
  cm4 vm create --count VMNUMBER [--debug] [--dryrun]
  cm4 vm start [--vms=VMLIST] [--debug] [--dryrun]
  cm4 vm stop [--vms=VMLIST] [--debug] [--dryrun]
  cm4 vm destroy [--vms=VMLIST] [--debug] [--dryrun]
  cm4 vm status [--vms=VMLIST] [--dryrun]
  cm4 vm list
  cm4 vm ssh NAME
  cm4 vm run COMMAND  [--vms=<vmList>]
  cm4 vm script run SCRIPT [--vms=<vmList>] [--dryrun]
  cm4 vcluster create virtual-cluster VIRTUALCLUSTER_NAME --clusters=CLUSTERS_LIST [--computers=COMPUTERS_LIST] [--debug]
  cm4 vcluster destroy virtual-cluster VIRTUALCLUSTER_NAME
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]]  [--download-later [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout+file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
  cm4 vcluster set-param runtime-config CONFIG_NAME PARAMETER VALUE
  cm4 vcluster destroy runtime-config CONFIG_NAME
  cm4 vcluster list virtual-clusters [DEPTH [default:1]]
  cm4 vcluster list runtime-configs [DEPTH [default:1]]
  cm4 vcluster run-script --script-path=SCRIPT_PATH --job-name=JOB_NAME --vcluster-name=VIRTUALCLUSTER_NAME --config-name=CONFIG_NAME --arguments=SET_OF_PARAMS --remote-path=REMOTE_PATH> --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
  cm4 vcluster fetch JOB_NAME
  cm4 vcluster clean-remote JOB_NAME PROCESS_NUM
  cm4 vcluster test-connection VIRTUALCLUSTER_NAME PROCESS_NUM
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
   Cloudmesh v4

"""
from docopt import docopt
from cm4.configuration.config import Config
import cm4.vagrant.vagrant
import cm4.vcluster.VirtualCluster
import cm4.data.data
import cm4.vm.Vm
import cm4


def process_arguments(arguments):
    version = cm4.__version__

    if arguments.get("--version"):
        print(version)

    elif arguments.get("vm"):
        cm4.vm.Vm.process_arguments(arguments)

    elif arguments.get("vagrant"):
        cm4.vagrant.vagrant.process_arguments(arguments)

    elif arguments.get("vcluster"):
        cm4.vcluster.VirtualCluster.process_arguments(arguments)

    elif arguments.get("data"):
        cm4.data.data.process_arguments(arguments)

    elif arguments.get("set"):
        config = Config()

        if arguments.get("cloud"):
            config.set("default.cloud", arguments.get("CLOUD"))

        elif arguments.get("group"):
            config.set("default.group", arguments.get("GROUP"))

        elif arguments.get("role"):
            config.set("default.role", arguments.get("ROLE"))

        elif arguments.get("cluster"):
            config.set("default.cluster", arguments.get("CLUSTER"))

        elif arguments.get("experiment"):
            config.set("default.experiment", arguments.get("EXPERIMENT"))

        elif arguments.get("host"):
            config.set("default.host", arguments.get("HOST"))

        elif arguments.get("--key") and arguments.get("--value"):
            config.set(arguments.get("--key"), arguments.get("--value"))

        print("Config has been updated.")


def main():
    """
    Main function for Cloudmesh 4. Expose `cm4` as an executable command.
    """
    version = cm4.__version__
    arguments = docopt(__doc__, version=version)
    process_arguments(arguments)


if __name__ == "__main__":
    main()
