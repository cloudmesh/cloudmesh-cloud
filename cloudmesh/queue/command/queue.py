from __future__ import print_function
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.shell.command import PluginCommand
from datetime import datetime
from cloudmesh.queue.api.Queue import Queue
from cloudmesh.variables import Variables
from cloudmesh.DEBUG import VERBOSE
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
            queue create --name=NAME --policy=POLICY --cloud=CLOUD
                [--charge=CHARGE]
                [--unit=UNIT]
            queue activate --cloud=CLOUD --queue=NAME
            queue deactivate --cloud=CLOUD --queue=NAME
            queue set --cloud=CLOUD --queue=QUEUE --param=PARAM --val=VALUE
            queue list clouds
            queue list queues --cloud=CLOUD
            queue list jobs --queue=QUEUE
            queue remove --name=NAME


          Arguments:
              FILE   a file name
              INPUT_TYPE  tbd

          Options:
              --depth=DEPTH   [default: 1]
              --format=FORMAT    [default: table]

          Description:

            This command creates a queue that is associated with a cloud.
            Each queue is associated with a cluster and can have several jobs
            in it.
            It is possible to get the list of the jobs in a queue either
            based on the queue name or based on the cluster name with which
            the queue is interacting.

          Examples:

        """

        queue = Queue()  # debug=arguments["--debug"])
        VERBOSE(arguments)
        implemented_policies = ['FIFO', 'FILO']
        variables = Variables()

        # docopt for some reason does not show all of the arguments in dot
        # format that's the reason I used -- format.
        if arguments.create and \
            arguments['--name'] and \
            arguments['--cloud'] and \
            arguments['--policy']:

            queue_name = arguments['--name']
            cloud_name = arguments['--cloud']
            policy = arguments['--policy']
            if policy.upper() not in ['FIFO', 'FILO']:
                Console.error("Policy {policy} not defined, currently "
                              "implemented policies are {policies} ".format(
                    policy=policy.upper(), policies=implemented_policies))
                return
            charge = arguments['--charge']
            unit = arguments['--unit']
            queue.create(queue_name,
                         cloud_name,
                         policy,
                         charge,
                         unit)
        elif arguments.activate and \
            arguments['--cloud'] and \
            arguments['--queue']:
            queue_found = queue.findQueue(arguments['--cloud'], arguments[
                '--queue'])
            if queue_found:
                queue.activate()

        elif arguments.deactivate and \
            arguments['--cloud'] and \
            arguments['--queue']:
            queue_found = queue.findQueue(arguments['--cloud'], arguments[
                '--queue'])
            if queue_found:
                queue.deactivate()

        elif arguments.list and \
            arguments.clouds:
            queue.findClouds()

        elif arguments.list and \
            arguments.queues:
            cloud = arguments['--cloud']
            queue.findQueues(cloud)

        elif arguments.list and arguments.jobs:
            queue.findQueues()

        elif arguments.set and arguments['--cloud'] and arguments['--queue'] \
            and arguments['--param'] and arguments['--val']:
            param = arguments['--param']
            val = arguments['--val']
            queue_found = queue.findQueue(arguments['--cloud'], arguments[
                '--queue'])
            if queue_found:
                queue.setParam(param,val)

        elif arguments.remove and arguments['--name']:
            name = arguments['--name']
            queue_found = queue.findQueue(name)
            if queue_found:
                queue.removeQueue()





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
        return '_' + str(datetime.now()).replace('-', ''). \
                         replace(' ', '_').replace(':', '') \
            [0:str(datetime.now()).replace('-', '').replace(' ', '_'). \
                   replace(':', '').index('.') + 3].replace('.', '')
