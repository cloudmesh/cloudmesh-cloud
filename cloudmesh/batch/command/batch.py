from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from datetime import datetime
from cloudmesh.batch.api.Batch import SlurmCluster


# from cloudmesh.batch.api.manager import Manager

# TODO does docopts allow to break line in multilpe?


"""
       ::

         Usage:
           batch job create JOB_NAME
                 --script=SCRIPT
                 --input-type=INPUT_TYPE
                 --cluster=CLUSTER_NAME
                 --job-script-path=SCRIPT_PATH
                 --remote-path=REMOTE_PATH
                 --local-path=LOCAL_PATH
                 [--argfile-path=ARGUMENT_FILE_PATH]
                 [--outfile-name=OUTPUT_FILE_NAME]
                 [--suffix=SUFFIX] [--overwrite]
           batch job run JOB_NAME
           batch fetch JOB_NAME
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
            batch job create JOB_NAME
                  --script=SLURM_SCRIPT_PATH
                  --input-type=INPUT_TYPE
                  --cluster=CLUSTER_NAME
                  --job-script-path=SCRIPT_PATH
                  --remote-path=REMOTE_PATH
                  --local-path=LOCAL_PATH
                  [--argfile-path=ARGUMENT_FILE_PATH]
                  [--outfile-name=OUTPUT_FILE_NAME]
                  [--suffix=SUFFIX] [--overwrite]
            batch job run JOB_NAME
            batch fetch JOB_NAME
            batch test CLUSTER_NAME
            batch set cluster CLUSTER_NAME PARAMETER VALUE
            batch set job JOB_NAME PARAMETER VALUE
            batch list clusters [DEPTH [default:1]]
            batch list jobs [DEPTH [default:1]]
            batch remove cluster CLUSTER_NAME
            batch remove job JOB_NAME
            batch clean JOB_NAME

          This command does some useful things.

          Arguments:
              FILE   a file name
              INPUT_TYPE  tbd

          Options:
              -f      specify the file

          Description:


            This command allows to submit batch jobs to queuing systems hosted
            in an HBC center as a service.

            We assume that a number of experiments are conducted with possibly
            running the script multiple times. Each experiment will safe the batch
            script in its own folder.

            The outout of the script can be safed in a destination folder. A virtual
            directory is used to coordinate all saved files.

            The files can be located due to the use of the firtual directiry on
            multiple different data or file servises

            Authentiaction to the Batch systems is done viw the underkaying center
            authentication. We assume that the user has an account to submit on
            these systems.

            (SSH, 2 factor, XSEDE-account) TBD.

        """
        arguments.FILE = arguments['--file'] or None

        print(arguments)

        debug = arguments["--debug"]

        if arguments.get("batch"):

            #
            # create slurm manager so it can be used in all commands
            #
            slurm_manager = SlurmCluster(debug=debug)

            # dont use print but use ,Consile.msg(), Consile.error(), Console.ok()

            if arguments.job and arguments.create and arguments.get("JOB_NAME"):
                job_name = arguments.get("JOB_NAME")
                slurm_script_path = arguments.get("--script")
                input_type = arguments.get("--input-type")
                assert input_type in ['params', 'params+file'], "Input type can be either params or params+file"
                if input_type == 'params+file':
                    assert arguments.get("--argfile-path") is not None, "Input type is params+file but the input \
                        filename is not specified"
                cluster_name = arguments.get("--cluster")
                job_script_path = arguments.get("--job-script-path")
                remote_path = arguments.get("--remote-path")
                local_path = arguments.get("--local-path")

                # TODO separate, make its own function?
                random_suffix = '_' + str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '')[
                                      0:str(datetime.now()).replace('-', '').replace(' ', '_').replace(':',
                                                                                                       '').index(
                                          '.') + 3].replace('.', '')
                suffix = random_suffix if arguments.get("suffix") is None else arguments.get("suffix")
                overwrite = False if type(arguments.get("--overwrite")) is None else arguments.get("--overwrite")
                argfile_path = '' if arguments.get("--argfile-path") is None else arguments.get("--argfile-path")
                slurm_manager.create(job_name,
                                     cluster_name,
                                     slurm_script_path,
                                     input_type,
                                     job_script_path,
                                     argfile_path,
                                     remote_path,
                                     local_path,
                                     suffix, overwrite)

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
            elif arguments.test:
                cluster_name = arguments.get("CLUSTER_NAME")
                slurm_manager.connection_test(cluster_name)
            elif arguments.clean:
                job_name = arguments.get("JOB_NAME")
                slurm_manager.clean_remote(job_name)
