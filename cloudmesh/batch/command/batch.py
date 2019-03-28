from __future__ import print_function
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.shell.command import PluginCommand
from datetime import datetime
from cloudmesh.batch.api.Batch import SlurmCluster
from cloudmesh.shell.variables import Variables
from cloudmesh.terminal.Terminal import VERBOSE
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.common.Printer import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from pathlib import Path

from pprint import pprint

# from cloudmesh.batch.api.manager import Manager

# TODO does docopts allow to break line in multilpe?


"""

REVISED COMMAND

       ::

         Usage:
 
       --destination=DESTINATION      # remote-path=REMOTE_PATH
                 --source=SOURCE                # local-path=LOCAL_PATH
                 [--argfile-path=ARGUMENT_FILE_PATH] # what is this
                 [--outfile-name=OUTPUT_FILE_NAME]   # what is this
                 [--suffix=SUFFIX] [--overwrite]     # what is this


      Old   
            --depth=DEPTH   [default: 1]
            batch job create JOB_NAME
                  [--script=SLURM_SCRIPT_PATH]
                  [--input-type=INPUT_TYPE]
                  [--cluster=CLUSTER_NAME]
                  [--job-script-path=SCRIPT_PATH]
                  [--remote-path=REMOTE_PATH]
                  [--local-path=LOCAL_PATH]
                  [--argfile-path=ARGUMENT_FILE_PATH]
                  [--outfile-name=OUTPUT_FILE_NAME]
                  [--suffix=SUFFIX] [--overwrite]
                  [--debug]
            batch job run JOB_NAME
            batch fetch JOB_NAME
            batch tester
            batch test CLUSTER_NAME
            batch set cluster CLUSTER_NAME PARAMETER VALUE
            batch set job JOB_NAME PARAMETER VALUE
            batch list clusters [DEPTH [default:1]]
            batch list jobs [DEPTH [default:1]]
            batch remove cluster CLUSTER_NAME
            batch remove job JOB_NAME
            batch clean JOB_NAME



"""



class BatchCommand(PluginCommand):

    # see also https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/HpcCommand.py
    # noinspection PyUnusedLocal
    @command
    def do_batch(self, args, arguments):
        """
        ::

          Usage:
            batch job create
                --name=NAME
                --cluster=CLUSTER
                --script=SCRIPT
                --executable=EXECUTABLE
                --destination=DESTINATION
                --source=SOURCE
                [--companion-file=COMPANION_FILE]
                [--outfile-name=OUTPUT_FILE_NAME]
                [--suffix=SUFFIX] [--overwrite]
            batch job run [--name=NAMES] [--format=FORMAT]
            batch job fetch [--name=NAMES]
            batch job remove [--name=NAMES]
            batch job clean [--name=NAMES]
            batch job set [--name=NAMES] PARAMETER=VALUE
            batch job list [--name=NAMES] [--depth=DEPTH]
            batch connection_test --job=JOB
            batch cluster list [--cluster=CLUSTERS] [--depth=DEPTH]
            batch cluster remove [--cluster=CLUSTERS]
            batch cluster set [--cluster=CLUSTERS] PARAMETER=VALUE

          Arguments:
              FILE   a file name
              INPUT_TYPE  tbd

          Options:
              -f      specify the file
              --depth=DEPTH   [default: 1]
              --format=FORMAT    [default: table]

          Description:

            This command allows to submit batch jobs to queuing systems hosted
            in an HBC center as a service.

            We assume that a number of experiments are conducted with possibly
            running the script multiple times. Each experiment will safe the batch
            script in its own folder.

            The outout of the script can be safed in a destination folder. A virtual
            directory is used to coordinate all saved files.

            The files can be located due to the use of the virtual directory on
            multiple different data or file services

            Authentication to the Batch systems is done viw the underlaying center
            authentication. We assume that the user has an account to submit on
            these systems.

            (SSH, 2 factor, XSEDE-account) TBD.

             batch job run [--name=NAMES] [--format=FORMAT]

                runs jobs with the given names


        """

        #
        # create slurm manager so it can be used in all commands
        #
        slurm_manager = SlurmCluster()  # debug=arguments["--debug"])

        arguments["--cloud"] = "test"
        arguments["NAME"] = "fix"

        map_parameters(arguments,
                       "cloud",
                       "name",
                       "cluster",
                       "script",
                       "type",
                       "destination",
                       "source",
                       "format")

        # if not arguments.create

        #    find cluster name from Variables()
        #    if no cluster is defined look it up in yaml in batch default:
        #    if not defined there fail

        #    clusters = Parameter.expand(arguments.cluster)
        #    name = Parameters.expand[argumnets.name)
        #    this will return an array of clusters and names of jobs and all cluster
        #    job or clusterc commands will be executed on them
        #    see the vm
        #
        #    if active: False in the yaml file for the cluster this cluster is not used and scipped.

        VERBOSE.print(arguments, verbose=9)

        variables = Variables()
        # do not use print but use ,Console.msg(), Console.error(), Console.ok()
        if arguments.tester:
            print("running ... ")
            slurm_manager.tester()
        elif arguments.run and arguments.job:

            # config = Config()["cloudmesh.batch"]

            names = Parameter.expand(arguments.name)

            # clouds, names = Arguments.get_cloud_and_names("refresh", arguments,
            #                                    variables)

            data = []
            for name in names:
                entry = SlurmCluster.job_specification()
                data.append(entry)

            '''
             data = {
            "cm": {
                "cloud": "karst_debug",
                "kind": "batch-job",
                "name": "job012",
            },
            "batch": {
                "source": "~/.cloudmesh/batch/dir",
                "destination": "~/.cloudmesh/dir/",
                "status": "running"
            }
            }'''

            try:
                raise NotImplementedError
            except Exception as e:
                Console.error("Haha", traceflag=True)

            pprint(data)
            print(Printer.flatwrite(
                data,
                order=["cm.name", "cm.kind", "batch.status"],
                header=["Name", "Kind", "Status"],
                output=arguments.format)
            )

            return ""
        # handling batch job create
        elif    arguments.job and \
                arguments.create and \
                arguments.name and \
                arguments.cluster and \
                arguments.script and \
                arguments['--executable'] and \
                arguments.destination and \
                arguments.source :
            job_name = arguments.name
            cluster_name = arguments.cluster
            script_path = Path(arguments.script)
            if not script_path.exists():
                raise FileNotFoundError
            executable_path = Path(arguments['--executable'])
            if not executable_path.exists():
                raise FileNotFoundError
            destination = Path(arguments.destination)
            if not destination.is_absolute():
                Console.error("destination path must be absolute",
                              traceflag=True)
                raise FileNotFoundError
            source = Path(arguments.source)
            if not source.exists():
                raise FileNotFoundError
            if arguments.experiment is None:
                experiment_name = 'job' + self.suffix_generator()
            else:
                experiment_name = arguments.experiment + self.suffix_generator()
            if arguments.get("--companion-file") is None:
                companion_file = Path()
            else:
                companion_file = Path(arguments.get("--companion-file"))
            slurm_manager.create(job_name,
                                 cluster_name,
                                 script_path,
                                 executable_path,
                                 destination,
                                 source,
                                 experiment_name,
                                 companion_file)

        elif arguments.remove:
            if arguments.cluster:
                slurm_manager.remove("cluster", arguments.get("CLUSTER_NAME"))
            if arguments.job:
                slurm_manager.remove("job", arguments.get("JOB_NAME"))

        elif arguments.list:
            max_depth = 1 if arguments.get("DEPTH") is None else int(arguments.get("DEPTH"))
            if arguments.get("clusters"):
                slurm_manager.list("clusters", max_depth)
            elif arguments.get("jobs"):
                slurm_manager.list("jobs", max_depth)

        elif arguments.set:
            if arguments.get("cluster"):
                cluster_name = arguments.get("CLUSTER_NAME")
                parameter = arguments.get("PARAMETER")
                value = arguments.get("VALUE")
                slurm_manager.set_param("cluster", cluster_name, parameter, value)

            if arguments.job:
                config_name = arguments.get("JOB_NAME")
                parameter = arguments.get("PARAMETER")
                value = arguments.get("VALUE")
                slurm_manager.set_param("job-metadata", config_name, parameter, value)
        elif arguments.start and arguments.job:
            job_name = arguments.get("JOB_NAME")
            slurm_manager.run(job_name)
        elif arguments.get("fetch"):
            job_name = arguments.get("JOB_NAME")
            slurm_manager.fetch(job_name)
        elif arguments.connection_test :
            slurm_manager.connection_test(arguments.job)
        elif arguments.clean:
            job_name = arguments.get("JOB_NAME")
            slurm_manager.clean_remote(job_name)

    def suffix_generator(self):
        """

        We do not want a random suffix, we want a numbered suffix. THis can be
        generated with the name method in the name.py function which can take a
        schema, so yo ucan create a schema for job or clusternames if needed
        Generate random suffix based on the time

        :return: string
        """
        return '_' + str(datetime.now()).replace('-', '').\
               replace(' ', '_').replace(':', '')\
               [0:str(datetime.now()).replace('-', '').replace(' ', '_').\
               replace(':','').index('.') + 3].replace('.', '')