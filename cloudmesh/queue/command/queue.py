from __future__ import print_function
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.shell.command import PluginCommand
from datetime import datetime
from cloudmesh.queue.api.Queue import Queue
from cloudmesh.shell.variables import Variables
from cloudmesh.terminal.Terminal import VERBOSE
from cloudmesh.management.configuration.arguments import Arguments
from cloudmesh.common.Printer import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
from pathlib import Path
from pprint import pprint

# from cloudmesh.batch.api.manager import Manager


class QueueCommand(PluginCommand):

    # see also https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/HpcCommand.py
    # noinspection PyUnusedLocal
    @command
    def do_queue(self, args, arguments):
        """
        ::

          Usage:
            queue create --name=NAME --policy=POLICY --cluster=CLUSTER
                [--charge=CHARGE]
                [--unit=UNIT]
            queue activate [--name=NAME]
            queue deactivate [--name=NAME]
            queue set unit
            queue connection_test --job=JOB
            queue cluster list [--cluster=CLUSTERS] [--depth=DEPTH]
            queue cluster remove [--cluster=CLUSTERS]
            queue cluster set [--cluster=CLUSTERS] PARAMETER=VALUE

          Arguments:
              FILE   a file name
              INPUT_TYPE  tbd

          Options:
              -f      specify the file
              --depth=DEPTH   [default: 1]
              --format=FORMAT    [default: table]

          Description:

            This command creates a queue that is associated with a cloud.

            We assume that a number of experiments are conducted with possibly
            running the script multiple times. Each experiment will save the
            batch script in its own folder.

            The output of the script can be saved in a destination folder. A virtual
            directory is used to coordinate all saved files.

            The files can be located due to the use of the virtual directory on
            multiple different data or file services

            Authentication to the Batch systems is done viw the underlaying HPC
            center authentication. We assume that the user has an account to
            submit on these systems.

            (SSH, 2 factor, XSEDE-account) TBD.

          Examples:

             LOTS OF DOCUMENTATION MISSING HERE

                [--companion-file=COMPANION_FILE]
                [--outfile-name=OUTPUT_FILE_NAME]
                [--suffix=SUFFIX] [--overwrite]




        """

        #
        # create slurm manager so it can be used in all commands
        #
        queue = Queue()  # debug=arguments["--debug"])

        # arguments["--cloud"] = "test"
        # arguments["NAME"] = "fix"

        # map_parameters(arguments,
        #                "cloud",
        #                "name",
        #                "cluster",
        #                "script",
        #                "type",
        #                "destination",
        #                "source",
        #                "format")

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
        implemented_policies = ['FIFO','FILO']
        variables = Variables()

        # docopt for some reason does not show all of the arguments in dot
        # format that's the reason I used -- format.
        if   arguments.create and \
             arguments['--name'] and \
             arguments['--cluster'] and \
             arguments['--policy']:

            queue_name = arguments['--name']
            cluster_name = arguments['--cluster']
            policy = arguments['--policy']
            if policy.upper() not in ['FIFO', 'FILO']:
                Console.error("Policy {policy} not defined, currently "
                              "implemented policies are {policies} ".format(
                    policy = policy.upper(),policies=implemented_policies))
                return
            charge = arguments['--charge']
            unit = arguments['--unit']
            queue.create(queue_name,
                         cluster_name,
                         policy,
                         charge,
                         unit)

        # elif arguments.remove:
        #     if arguments.cluster:
        #         slurm_manager.remove("cluster", arguments.get("CLUSTER_NAME"))
        #     if arguments.job:
        #         slurm_manager.remove("job", arguments.get("JOB_NAME"))
        #
        # elif arguments.list:
        #     max_depth = 1 if arguments.get("DEPTH") is None else int(arguments.get("DEPTH"))
        #     if arguments.get("clusters"):
        #         slurm_manager.list("clusters", max_depth)
        #     elif arguments.get("jobs"):
        #         slurm_manager.list("jobs", max_depth)
        #
        # elif arguments.set:
        #     if arguments.get("cluster"):
        #         cluster_name = arguments.get("CLUSTER_NAME")
        #         parameter = arguments.get("PARAMETER")
        #         value = arguments.get("VALUE")
        #         slurm_manager.set_param("cluster", cluster_name, parameter, value)
        #
        #     if arguments.job:
        #         config_name = arguments.get("JOB_NAME")
        #         parameter = arguments.get("PARAMETER")
        #         value = arguments.get("VALUE")
        #         slurm_manager.set_param("job-metadata", config_name, parameter, value)
        # elif arguments.start and arguments.job:
        #     job_name = arguments.get("JOB_NAME")
        #     slurm_manager.run(job_name)
        # elif arguments.get("fetch"):
        #     job_name = arguments.get("JOB_NAME")
        #     slurm_manager.fetch(job_name)
        # elif arguments.connection_test :
        #     slurm_manager.connection_test(arguments.job)
        # elif arguments.clean:
        #     job_name = arguments.get("JOB_NAME")
        #     slurm_manager.clean_remote(job_name)

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