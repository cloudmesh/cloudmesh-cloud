from datetime import datetime

import hostlist
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.vcluster.api.VirtualCluster import VirtualCluster


class VclusterCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_vcluster(self, args, arguments):
        """
        ::

          Usage:
          
            vcluster create cluster CLUSTER_NAME --clusters=CLUSTERS_LIST [--computers=COMPUTERS_LIST] [--debug]
            vcluster destroy cluster CLUSTER_NAME
            vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
            vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
            vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]]  [--download-later [default=True]]  [--debug]
            vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
            vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout+file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-later [default=True]]  [--debug]
            vcluster set-param runtime-config CONFIG_NAME PARAMETER VALUE
            vcluster destroy runtime-config CONFIG_NAME
            vcluster list clusters [DEPTH [default:1]]
            vcluster list runtime-configs [DEPTH [default:1]]
            vcluster run-script --script-path=SCRIPT_PATH --job-name=JOB_NAME --vcluster-name=CLUSTER_NAME --config-name=CONFIG_NAME --arguments=SET_OF_PARAMS --remote-path=REMOTE_PATH --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
            vcluster fetch JOB_NAME
            vcluster clean-remote JOB_NAME PROCESS_NUM
            vcluster test-connection CLUSTER_NAME PROCESS_NUM

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """

        print(arguments)

        debug = arguments["--debug"]

        if arguments.get("vcluster"):
            vcluster_manager = VirtualCluster(debug=debug)
            if arguments.get("create"):
                if arguments.get("cluster") and arguments.get("--clusters"):
                    clusters = hostlist.expand_hostlist(
                        arguments.get("--clusters"))
                    computers = hostlist.expand_hostlist(
                        arguments.get("--computers"))
                    vcluster_manager.create(arguments.get("CLUSTER_NAME"),
                                            cluster_list=clusters,
                                            computer_list=computers)
                elif arguments.get("runtime-config") and arguments.get(
                    "CONFIG_NAME") and arguments.get("PROCESS_NUM"):
                    config_name = arguments.get("CONFIG_NAME")
                    proc_num = int(arguments.get("PROCESS_NUM"))
                    download_proc_num = 1 if arguments.get(
                        "--fetch-proc-num") is None else \
                        int(arguments.get("--fetch-proc-num"))
                    download_later = True if arguments.get(
                        "--download-later") is True else False
                    input_type = ""
                    output_type = ""
                    if arguments.get("in:params") and arguments.get(
                        "out:stdout"):
                        input_type = "params"
                        output_type = "stdout"
                    elif arguments.get("in:params") and arguments.get(
                        "out:file"):
                        input_type = "params"
                        output_type = "file"
                    elif arguments.get("in:params+file") and arguments.get(
                        "out:stdout"):
                        input_type = "params+file"
                        output_type = "stdout"
                    elif arguments.get("in:params+file") and arguments.get(
                        "out:file"):
                        input_type = "params+file"
                        output_type = "file"
                    elif arguments.get("in:params+file") and arguments.get(
                        "out:stdout+file"):
                        input_type = "params+file"
                        output_type = "stdout+file"
                    vcluster_manager.create(config_name, proc_num,
                                            download_proc_num, download_later,
                                            input_type,
                                            output_type)

            elif arguments.get("destroy"):
                if arguments.get("cluster"):
                    vcluster_manager.destroy("virtual-cluster",
                                             arguments.get("CLUSTER_NAME"))
                elif arguments.get("runtime-config"):
                    vcluster_manager.destroy("runtime-config",
                                             arguments.get("CONFIG_NAME"))

            elif arguments.get("list"):
                if arguments.get("clusters"):
                    max_depth = 1 if arguments.get("DEPTH") is None else int(
                        arguments.get("DEPTH"))
                    vcluster_manager.list("virtual-clusters", max_depth)
                elif arguments.get("runtime-configs"):
                    max_depth = 1 if arguments.get("DEPTH") is None else int(
                        arguments.get("DEPTH"))
                    vcluster_manager.list("runtime-configs", max_depth)

            elif arguments.get("set-param"):
                if arguments.get("clusters"):
                    cluster_name = arguments.get("CLUSTER_NAME")
                    parameter = arguments.get("PARAMETER")
                    value = arguments.get("VALUE")
                    vcluster_manager.set_param("virtual-clusters", cluster_name,
                                               parameter, value)

                if arguments.get("runtime-config"):
                    config_name = arguments.get("CONFIG_NAME")
                    parameter = arguments.get("PARAMETER")
                    value = arguments.get("VALUE")
                    vcluster_manager.set_param("runtime-config", config_name,
                                               parameter, value)
            elif arguments.get("run-script"):
                job_name = arguments.get("--job-name")
                cluster_name = arguments.get("--vcluster-name")
                config_name = arguments.get("--config-name")
                script_path = arguments.get("--script-path")
                remote_path = arguments.get("--remote-path")
                local_path = arguments.get("--local-path")
                random_suffix = '_' + str(datetime.now()).replace('-',
                                                                  '').replace(
                    ' ', '_').replace(':', '')[
                                      0:str(datetime.now()).replace('-',
                                                                    '').replace(
                                          ' ', '_').replace(':', '').index(
                                          '.') + 3].replace('.', '')
                suffix = random_suffix if arguments.get(
                    "suffix") is None else arguments.get("suffix")
                params_list = arguments.get("--arguments").split(',')
                overwrite = False if type(
                    arguments.get("--overwrite")) is None else arguments.get(
                    "--overwrite")
                argfile_path = '' if arguments.get(
                    "--argfile-path") is None else arguments.get(
                    "--argfile-path")
                outfile_name = '' if arguments.get(
                    "--outfile-name") is None else arguments.get(
                    "--outfile-name")
                vcluster_manager.run(job_name, cluster_name, config_name,
                                     script_path, argfile_path, outfile_name,
                                     remote_path, local_path, params_list,
                                     suffix, overwrite)
            elif arguments.get("fetch"):
                job_name = arguments.get("JOB_NAME")
                vcluster_manager.fetch(job_name)
            elif arguments.get("test-connection"):
                vcluster_name = arguments.get("CLUSTER_NAME")
                proc_num = int(arguments.get("PROCESS_NUM"))
                vcluster_manager.connection_test(vcluster_name, proc_num)
            elif arguments.get("clean-remote"):
                job_name = arguments.get("JOB_NAME")
                proc_num = int(arguments.get("PROCESS_NUM"))
                vcluster_manager.clean_remote(job_name, proc_num)
