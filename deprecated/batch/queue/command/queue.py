from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from datetime import datetime
from deprecated.batch.queue import Queue
from cloudmesh.variables import Variables
from cloudmesh.DEBUG import VERBOSE
from cloudmesh.common.console import Console


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
            queue activate --name=NAME
            queue deactivate --name=NAME
            queue set PARAMETER=VALUE --name=NAME
            queue list all
            queue list jobs [--cluster=CLUSTERS] [--name=NAME]
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
            arguments['--cluster'] and \
            arguments['--policy']:

            queue_name = arguments['--name']
            cluster_name = arguments['--cluster']
            policy = arguments['--policy']
            if policy.upper() not in ['FIFO', 'FILO']:
                Console.error("Policy {policy} not defined, currently "
                              "implemented policies are {policies} ".format(
                    policy=policy.upper(), policies=implemented_policies))
                return
            charge = arguments['--charge']
            unit = arguments['--unit']
            queue.create(queue_name,
                         cluster_name,
                         policy,
                         charge,
                         unit)
        elif arguments.activate and \
            arguments['--name']:
            queue.findQueueByName(arguments['--name'])
            queue.activate()

        elif arguments.deactivate and \
            arguments['--name']:
            queue.findQueueByName(arguments['--name'])
            queue.deactivate()

        elif arguments.list and \
            arguments.jobs:

            if arguments['--name']:
                name = arguments['--name']
                queue.findQueueByName(name)
                queue.listJobs()
            elif arguments['--cluster']:
                cluster = arguments['--cluster']
                queue.findQueueByName(cluster)
                queue.listJobs()

        elif arguments.list and arguments.all:
            queue.findAllQueues()

        elif arguments.set and arguments['--name']:
            name = arguments['--name']
            param = arguments.get("PARAMETER")
            val = arguments.get("PARAMETER")
            queue.findQueueByName(name)
            queue.setParam(param,val)

        elif arguments.remove and arguments['--name']:
            name = arguments['--name']
            queue.findQueueByName(name)
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
