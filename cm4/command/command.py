"""Cloudmesh 4

::

    Usage:
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
      cm4 aws run command COMMAND [--vm=name]
      cm4 aws run script SCRIPT [--vm=name]
      cm4 batch create-job JOB_NAME --slurm-script=SLURM_SCRIPT_PATH --input-type=INPUT_TYPE --slurm-cluster=SLURM_CLUSTER_NAME --job-script-path=SCRIPT_PATH --remote-path=REMOTE_PATH --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
      cm4 batch run-job JOB_NAME
      cm4 batch fetch JOB_NAME
      cm4 batch test-connection SLURM_CLUSTER_NAME
      cm4 batch set-param slurm-cluster CLUSTER_NAME PARAMETER VALUE
      cm4 batch set-param job-metadata JOB_NAME PARAMETER VALUE
      cm4 batch list slurm-clusters [DEPTH [default:1]]
      cm4 batch list jobs [DEPTH [default:1]]
      cm4 batch remove slurm-cluster CLUSTER_NAME
      cm4 batch remove job JOB_NAME
      cm4 batch clean-remote JOB_NAME
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
import cm4.vcluster.VirtualCluster
import cm4.batch.Batch
import cm4.data.data
import cm4.vm.Vm
import cm4.openstack.OpenstackCM
import cm4

#
# TODO: BUG: aws has been removed
#
#import cm4.aws.CommandAWS
from cm4.mongo.MongoDBController import MongoDBController
from pprint import pprint
from cloudmesh.common.dotdict import dotdict


def process_arguments(arguments):
    version = cm4.__version__

    arguments = dotdict(arguments)

    if arguments.get("--version"):
        print(version)

    elif arguments.get('aws'):
        # cm4.aws.CommandAWS.process_arguments(arguments)
        raise NotImplementedError ("THERE IS A BUG HERE, CONTACT DAVID")

    elif arguments.get("batch"):
        cm4.batch.Batch.process_arguments(arguments)

    elif arguments.get("openstack"):
        cm4.openstack.OpenstackCM.process_arguments(arguments)

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
