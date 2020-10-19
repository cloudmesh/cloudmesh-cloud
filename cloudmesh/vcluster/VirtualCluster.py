#!/usr/bin/env python3


import ntpath
import os
import subprocess
import time
from multiprocessing import Pool, Manager

from cloudmesh.configuration.Config import Config
from cloudmesh.management.configuration.generic_config import GenericConfig


# noinspection PyPep8
class VirtualCluster(object):

    def __init__(self, debug):
        """
        Initializes the virtualcluster class

        :param debug: switch the debug information on and off
        """
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.workspace = os.path.join(current_path,
                                      "vcluster_workspace/now.yaml")
        if not os.path.exists(os.path.dirname(self.workspace)):
            os.makedirs(os.path.dirname(self.workspace))
        self.cm_config = Config()
        self.vcluster_config = GenericConfig(self.workspace)
        self.debug = debug
        self.all_pids = []
        self.virt_cluster = {}
        self.runtime_config = {}
        self.job_metadata = {}

    def _config_validator(self):
        """
        validates the configuration of a run based on the information about its virtual cluster, runtime configuration
        and the job metadata

        :return:
        """
        job_metadata = self.job_metadata
        virt_cluster = self.virt_cluster
        runtime_config = self.runtime_config
        for node in virt_cluster:
            if 'name' not in virt_cluster[node].keys():
                raise ValueError(
                    " node {}: 'name' keyword, indicating hostname is missing from".format(
                        node))
            if 'sshconfigpath' not in virt_cluster[node]['credentials'].keys():
                raise ValueError(
                    "%s: 'sshconfigpath' keyword is missing" % node)
            if not os.path.isfile(os.path.expanduser(
                virt_cluster[node]['credentials']['sshconfigpath'])):
                raise ValueError(
                    "%s: The ssh config file %s does not exists" % (
                        node, virt_cluster[node] \
                            ['credentials']['sshconfigpath']))
        if not os.path.isfile(os.path.expanduser(job_metadata['script_path'])):
            raise ValueError("The script file %s does not exists" % (
                job_metadata['script_path']))
        if runtime_config['input-type'] == 'params+file':
            if not os.path.isfile(
                os.path.expanduser(job_metadata['argfile_path'])):
                raise ValueError("The arg file %s does not exists" % (
                    job_metadata['arg_file_path']))

    def _clean_remote_in_parallel(self, target_node, remote_path):
        """
        This method is used to spawn processes to clean the remotes of a particular job.

        :param target_node: the node on which the data is going to be removed
        :param remote_path: path of the data to be removed
        :return:
        """
        target_node_info = self.virt_cluster[target_node]
        ssh_caller = lambda *x: self._ssh(target_node_info['name'],
                                          os.path.expanduser(
                                              target_node_info['credentials'] \
                                                  ['sshconfigpath']), *x)
        ssh_caller('rm -rf {}'.format(remote_path))
        if len(ssh_caller('ls {}'.format(remote_path))) == 0:
            print("Node {} cleaned successfully.".format(target_node))
        else:
            print("Error: Node {} could not be cleaned.".format(target_node))

    def _connection_test_in_parallel(self, target_node):
        """
        This method is used to test the connection to cluster nodes in parallel

        :param target_node: the node to which the connection is going to be tested
        :return:
        """
        target_node_info = self.virt_cluster[target_node]
        ssh_caller = lambda *x: self._ssh(target_node_info['name'],
                                          os.path.expanduser(
                                              target_node_info['credentials'] \
                                                  ['sshconfigpath']), *x)
        if len(ssh_caller('uname -a')) > 0:
            print("Node {} is accessible.".format(target_node))
        else:
            print("Error: Node {} cannot be accessed.".format(target_node))

    def _create_config(self,
                       config_name,
                       proc_num,
                       download_proc_num,
                       download_later,
                       input_type,
                       output_type):
        """
        This method is used to create a runtime-configuration.

        :param config_name: name of the runtime configuration
        :param proc_num: number of processes to be spawned in that runtime for submitting the jobs
        :param download_proc_num: number number of processes to be spawned in that runtime for fetching the results
        :param download_later: a flag indicating whether or not the script should wait for the results after the scripts are submitted
        :param input_type: type of the input of the script to be run remotely
        :param output_type: type of the output of the script to be run remotely
        :return:
        """
        config_tosave = {config_name: {}}
        config_tosave[config_name].update({"proc_num": proc_num,
                                           "download_proc_num": download_proc_num,
                                           "download-later": download_later,
                                           "input-type": input_type,
                                           "output-type": output_type})
        self.vcluster_config.deep_set(['runtime-config'], config_tosave)
        print("Runtime-configuration created/replaced successfully.")

    def _create_vcluster(self, vcluster_name, cluster_list=(),
                         computer_list=()):
        """
        This method is used to create a virtual cluster

        :param vcluster_name: name of the virtual cluster
        :param cluster_list: list of the clusters to be added to the
               virtual cluster
        :param computer_list: list of the computers to be used from the
               previous parameter (cluster_list). If the computer_list is left
               empty, all of the computers will be used
        :return:
        """
        vcluster_tosave = {vcluster_name: {}}
        for cluster in cluster_list:
            for computer in self.cm_config.get('cluster.{}'.format(cluster)):
                if computer in computer_list or computer_list == '':
                    vcluster_tosave[vcluster_name].update({computer: dict(
                        self.cm_config.get('cluster.{}.{}'.format(
                            cluster, computer)))})
        self.vcluster_config.deep_set(['virtual-cluster'], vcluster_tosave)
        print("Virtual cluster created/replaced successfully.")

    @staticmethod
    def _execute_in_parallel(func_args):
        """
        This is a method used for running methods in parallel

        :param func_args:
        :return:
        """
        target_class = func_args[0]
        method_to_call = getattr(target_class, func_args[1])
        args = list(func_args[2:])
        return method_to_call(*args)

    def _fetch_results_in_parallel(self, job_metadata, node_pid_tuple,
                                   all_pids):
        """
        This method is used to fetch the results from remote nodes.

        :param job_metadata: the dictionary containing the information about the previously submitted job
        :param node_pid_tuple: the tuple containing destination node, destination pid and destination node index when the job was submitted
        :param all_pids:
        :return:
        """
        dest_node = node_pid_tuple[0]
        dest_pid = node_pid_tuple[1]
        node_idx = node_pid_tuple[2]
        dest_node_info = self.virt_cluster[dest_node]
        ssh_caller = lambda *x: self._ssh(dest_node_info['name'],
                                          os.path.expanduser(
                                              dest_node_info['credentials'] \
                                                  ['sshconfigpath']), *x)
        scp_caller = lambda *x: self._scp(dest_node_info['name'],
                                          os.path.expanduser(
                                              dest_node_info['credentials'] \
                                                  ['sshconfigpath']), *x)
        ps_output = ssh_caller('ps', '-ef', '|', 'grep', dest_pid.strip('\n'),
                               '|', 'grep -v grep')
        if len(ps_output) == 0 and node_pid_tuple in [pid for pid in all_pids]:
            if not os.path.exists(job_metadata['local_path']):
                os.makedirs(job_metadata['local_path'])
            if self.runtime_config['output-type'] == 'stdout':
                scp_caller('%s:%s' % (dest_node_info['name'],
                                      os.path.join(job_metadata['remote_path'],
                                                   self.add_suffix_to_path(
                                                       'outputfile_%d' % node_idx,
                                                       job_metadata[
                                                           'suffix']))),
                           os.path.join(job_metadata['local_path'], ''))
            elif self.runtime_config['output-type'] in ['file', 'stdout+file']:
                nested_remote_path = os.path.join(job_metadata['remote_path'],
                                                  'run{}'.format(node_idx))
                scp_caller('-r', '%s:%s' % (
                    dest_node_info['name'], nested_remote_path),
                           os.path.join(job_metadata \
                                            [
                                            'local_path'],
                                        ''))
            all_pids.remove((dest_node, dest_pid, node_idx))
            print("Results collected from %s." % dest_node)

    def _run_remote_job_in_parallel(self, job_metadata, param_idx, params,
                                    all_pids):
        """
        This method is used to spawn remote processes in parallel

        :param job_metadata: contains the information about the job
        :param param_idx: index of the parameters inputted as argument
        :param params: the parameters inputted as argument for this run
        :param all_pids: the manager used to take all pids of all submitted jobs
        :return:
        """
        available_nodes_num = len(list(self.virt_cluster.keys()))
        target_node_idx = param_idx % available_nodes_num
        target_node_key = list(self.virt_cluster.keys())[target_node_idx]
        target_node = self.virt_cluster[target_node_key]
        remote_pid = []
        ssh_caller = lambda *x: self._ssh(target_node['name'],
                                          os.path.expanduser(
                                              target_node['credentials'] \
                                                  ['sshconfigpath']), *x)
        scp_caller = lambda *x: self._scp(target_node['name'],
                                          os.path.expanduser(
                                              target_node['credentials'] \
                                                  ['sshconfigpath']), *x)

        # directory_check = ssh_caller('if test -d %s; then echo "exist"; fi' % job_metadata['remote_path'])
        # if len(directory_check) == 0:
        ssh_caller('cd %s && mkdir job%s' % (
            job_metadata['raw_remote_path'], job_metadata['suffix']), True)
        if self.runtime_config['output-type'].lower() in ['file',
                                                          'stdout+file']:
            ssh_caller(
                "cd {} && mkdir run{}".format(job_metadata['remote_path'],
                                              param_idx))
            nested_remote_path = os.path.join(job_metadata['remote_path'],
                                              'run{}'.format(param_idx),
                                              job_metadata[
                                                  'script_name_with_suffix'])
            scp_caller(job_metadata['script_path'],
                       '%s:%s' % (target_node['name'], nested_remote_path))
            ssh_caller('chmod +x', nested_remote_path)
            if self.runtime_config['input-type'].lower() == 'params+file':
                scp_caller(job_metadata['argfile_path'],
                           '%s:%s' % (target_node['name'],
                                      os.path.join(job_metadata['remote_path'],
                                                   'run{}'.format(param_idx),
                                                   job_metadata[
                                                       'argfile_name'])))
        else:
            scp_caller(job_metadata['script_path'], '%s:%s' % (
                target_node['name'], job_metadata['remote_script_path']))
            ssh_caller('chmod +x', job_metadata['remote_script_path'])
            if self.runtime_config['input-type'].lower() == 'params+file':
                scp_caller(job_metadata['argfile_path'], '%s:%s' % (
                    target_node['name'], job_metadata['remote_path']))

        if self.runtime_config['output-type'].lower() == 'stdout':
            remote_pid = ssh_caller(
                'cd %s && nohup %s %s > %s 2>&1 </dev/null& echo $!' % (
                    job_metadata['remote_path'],
                    job_metadata['remote_script_path'],
                    params,
                    os.path.join(job_metadata['remote_path'],
                                 self.add_suffix_to_path(
                                     'outputfile_%d' % \
                                     param_idx,
                                     job_metadata['suffix']))))
        elif self.runtime_config['output-type'].lower() == 'stdout+file':
            remote_pid = ssh_caller(
                'cd %s && nohup %s %s > %s 2>&1 </dev/null& echo $!' % \
                (os.path.join(job_metadata['remote_path'],
                              'run{}'.format(param_idx)),
                 os.path.join(job_metadata['remote_path'],
                              'run{}'.format(param_idx),
                              job_metadata['script_name_with_suffix']), params,
                 os.path.join(
                     job_metadata['remote_path'], 'run{}'.format(param_idx),
                     self.add_suffix_to_path('outputfile_%d' % param_idx,
                                             job_metadata['suffix']))))
        elif self.runtime_config['output-type'].lower() == 'file':
            remote_pid = ssh_caller('cd %s && nohup ./%s %s >&- & echo $!' % (
                os.path.join(job_metadata['remote_path'],
                             'run{}'.format(param_idx)),
                job_metadata['script_name_with_suffix'],
                params))
        all_pids.append((target_node_key, remote_pid, param_idx))
        print(
            'Remote Pid on %s: %s' % (target_node_key, remote_pid.strip('\n')))

    @staticmethod
    def _ssh(hostname, sshconfigpath, *args):
        """
        This method is used to create remove ssh connections

        :param hostname: hostname
        :param sshconfigpath: path to sshconfig for connecting to remote node
        :param args: the argument to be submitted via ssh
        :return:
        """
        hide_errors_flag = False
        if type(args[-1]) == bool:
            hide_errors_flag = True
            args = args[:-1]
        ssh = subprocess.Popen(["ssh", hostname, '-F', sshconfigpath, *args],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readline()
        if not result:
            error = ssh.stderr.readlines()
            if len(error) > 0 and hide_errors_flag == False:
                print("ERROR in host %s: %s" % (hostname, error))
            return []
        else:
            try:
                return ''.join([chr(x) for x in result])
            except AttributeError:
                return [result.decode('utf-8').strip('\n')]

    @staticmethod
    def _scp(hostname, sshconfigpath, *args):
        """
        This method is used for scp from and to remote

        :param hostname: hostname
        :param sshconfigpath: ssh config file
        :param args:arguments for using while copying
        :return:
        """
        ssh = subprocess.Popen(["scp", '-F', sshconfigpath, *args],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        middle_result = ssh.stdout.readlines()
        if not middle_result:
            error = ssh.stderr.readlines()
            if len(error) > 0:
                print("ERROR in host %s: %s" % (hostname, error))

    @staticmethod
    def add_suffix_to_path(path, suffix):
        """
        This method is used to add suffix to a path

        :param path: path
        :param suffix: suffix
        :return:
        """
        dir_path = os.path.dirname(path)
        full_filename = os.path.basename(path)
        filename, fileextention = os.path.splitext(full_filename)
        full_filename_new = filename + suffix + fileextention
        new_path = os.path.join(dir_path, full_filename_new)
        return new_path

    def clean_remote(self, job_name, proc_num):
        """
        This method is used to spawn processes for cleaning the remote nodes

        :param job_name: name of previously submitted job for which the nodes are going to be cleaned
        :param proc_num: number of processes used for cleaning the remote nodes
        :return:
        """
        job_metadata = self.vcluster_config.get('job-metadata')[job_name]
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[
            job_metadata['cluster_name']]
        remote_path = job_metadata['remote_path']
        all_jobs = [(self, '_clean_remote_in_parallel', node, remote_path) for
                    node in list(self.virt_cluster)]
        pool = Pool(processes=proc_num)
        pool.map(self._execute_in_parallel, all_jobs)

    def connection_test(self, vcluster_name, proc_num):
        """
        This method is used for spawning processes for testing the connections to remote nodes of a vcluster

        :param vcluster_name: name of the virtual cluster the nodes of which are going to be tested
        :param proc_num: number of processes used for testing the remote nodes
        :return:
        """
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[
            vcluster_name]
        all_jobs = [(self, '_connection_test_in_parallel', node) for node in
                    list(self.virt_cluster)]
        pool = Pool(processes=proc_num)
        pool.map(self._execute_in_parallel, all_jobs)

    def create(self, *args, **kwargs):
        """
        This is a caller for creator functions including config creator and vcluster creator

        :param args:
        :param kwargs:
        :return:
        """
        if len(args) > 5:
            self._create_config(*args)
        else:
            self._create_vcluster(*args, **kwargs)

    def destroy(self, target, key):
        """
        Used to remove virtual clusters and runtime configs

        :param target: type of entity to be removed
        :param key: keyname of the entity to be removed
        :return:
        """
        if target == 'virtual-cluster':
            self.vcluster_config.remove(['virtual-cluster'], key)
            print("Virtual-cluster {} destroyed successfully.".format(key))
        elif target == 'runtime-config':
            self.vcluster_config.remove(['runtime-config'], key)
            print(
                "Runtime-configuration {} destroyed successfully.".format(key))
        else:
            raise ValueError("Target of destroying not found.")

    def fetch(self, job_name):
        """
        This method is used to fetch results from remote nodes

        :param job_name: the previously submitted job name
        :return:
        """
        job_metadata = self.vcluster_config.get('job-metadata')[job_name]
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[
            job_metadata['cluster_name']]
        self.runtime_config = self.vcluster_config.get('runtime-config')[
            job_metadata['config_name']]
        loaded_all_pids = [tuple(x) for x in job_metadata['nodes-pids']]
        all_pids = Manager().list()
        all_pids.extend(loaded_all_pids)
        pool = Pool(processes=self.runtime_config['download_proc_num'])
        print("collecting results")
        while len(all_pids) > 0:
            time.sleep(1)
            all_running_jobs = [(self, '_fetch_results_in_parallel',
                                 job_metadata, node_pid_tuple, all_pids) for \
                                node_pid_tuple in loaded_all_pids if
                                node_pid_tuple in all_pids]
            pool.map(self._execute_in_parallel, all_running_jobs)
            print("waiting for other results if any...")
        print("All of the remote results collected.")

    def list(self, target, max_depth, current_depth=1, input_dict=None):
        """
        listing the current virtual clusters based on the vcluster_conf file.

        :param target: name of the virtual cluster to be listed
        :param max_depth: depth of information to be shown
        :param input_dict: used for recursion for depth of higher than 1
        :param current_depth: current depth of printing information
        :return:
        """
        if target == 'virtual-clusters' and input_dict is None:
            input_dict = self.vcluster_config.get('virtual-cluster')
        elif target == 'runtime-configs' and input_dict is None:
            input_dict = self.vcluster_config.get('runtime-config')
        elif input_dict is None:
            raise ValueError("Target of listing not found.")

        if max_depth >= current_depth:
            if type(input_dict) == dict:
                for key in input_dict:
                    key_to_print = key + ':' if max_depth >= current_depth else key
                    indent = current_depth if current_depth > 1 else current_depth - 1
                    print('\t' * indent, key_to_print)
                    if type(input_dict.get(key)) != dict:
                        print('\t' * (indent + 1), input_dict.get(key))
                    else:
                        for value in input_dict.get(key):
                            value_to_print = value + ':' if max_depth > current_depth else value
                            print('\t' * (indent + 1), value_to_print)
                            self.list(target, max_depth,
                                      input_dict=input_dict[key][value],
                                      current_depth=current_depth + 1)
            else:
                indent = current_depth if current_depth > 1 else current_depth - 1
                print('\t' * indent, input_dict)

    def run(self,
            job_name,
            cluster_name,
            config_name,
            script_path,
            argfile_path,
            outfile_name,
            remote_path,
            local_path,
            params_list,
            suffix,
            overwrite):
        """
        This method is used to create a job, validate it and run it on remote nodes

        :param job_name: name of the job to create
        :param cluster_name: cluster on which the job is gonna run
        :param config_name: name of the configuration based on which the job is going to run
        :param script_path: path of the script to be run remotely
        :param argfile_path: path of the file that has to be passed to the file as an argument if any
        :param outfile_name: output filename resulted from running the script , if any
        :param remote_path: path in the remotes on which the script is gonna be copied to and ran from
        :param local_path: local path to which the results are gonna be copied
        :param params_list: list of the parameters that are going to be passed to the script if any
        :param suffix: suffix of the filenames in the job
        :param overwrite: if the job already exists, this flag overwrites the previous job with the same name
        :return:
        """
        if params_list is None:
            raise ValueError('param-list is not set. This value determines how many instance of the target application \
            will run remotely. Therefore, even if the parameter is empty, add commas for every run you expect.')
        if self.vcluster_config.get('job-metadata') is not None and job_name in \
            list(self.vcluster_config.get(
                'job-metadata').keys()) and overwrite is False:
            raise RuntimeError("The job {} exists in the configuration file, if you want to overwrite the job, \
            use --overwrite argument.".format(job_name))
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[
            cluster_name]
        self.runtime_config = self.vcluster_config.get('runtime-config')[
            config_name]
        job_metadata = {job_name: {}}
        job_metadata[job_name]['suffix'] = suffix
        job_metadata[job_name]['cluster_name'] = cluster_name
        job_metadata[job_name]['config_name'] = config_name
        job_metadata[job_name]['raw_remote_path'] = remote_path
        job_metadata[job_name]['script_path'] = os.path.abspath(script_path)
        job_metadata[job_name]['argfile_path'] = argfile_path
        job_metadata[job_name]['argfile_name'] = ntpath.basename(argfile_path)
        if len(job_metadata[job_name]['argfile_name']) > 0:
            job_metadata[job_name]['params_list'] = [
                '{} {}'.format(job_metadata[job_name]['argfile_name'], x) \
                for x in params_list]
        else:
            job_metadata[job_name]['params_list'] = params_list
        job_metadata[job_name]['outfile_name'] = outfile_name
        job_metadata[job_name]['script_name'] = ntpath.basename(script_path)
        job_metadata[job_name][
            'script_name_with_suffix'] = self.add_suffix_to_path(
            job_metadata[job_name] \
                ['script_name'], suffix)
        job_metadata[job_name]['remote_path'] = os.path.join(remote_path,
                                                             'job' + suffix, '')
        job_metadata[job_name]['remote_script_path'] = os.path.join(
            job_metadata[job_name]['remote_path'],
            job_metadata[job_name]['script_name_with_suffix'])
        job_metadata[job_name]['local_path'] = local_path
        self.job_metadata = job_metadata[job_name]
        self._config_validator()
        self.vcluster_config.deep_set(['job-metadata'], job_metadata)
        all_pids = Manager().list()
        all_jobs = [(
            self, '_run_remote_job_in_parallel', job_metadata[job_name],
            param_idx, param, all_pids) for \
            param_idx, param in
            enumerate(job_metadata[job_name]['params_list'])]
        pool = Pool(processes=self.runtime_config['proc_num'])
        pool.map(self._execute_in_parallel, all_jobs)
        self.all_pids = all_pids
        self.vcluster_config.deep_set(['job-metadata', job_name, 'nodes-pids'],
                                      [pid for pid in all_pids])
        if not self.runtime_config['download-later']:
            pool = Pool(processes=self.runtime_config['download_proc_num'])
            print("collecting results")
            while len(all_pids) > 0:
                time.sleep(3)
                all_running_jobs = [
                    (self, '_fetch_results_in_parallel', job_metadata[job_name],
                     node_pid_tuple, all_pids) for node_pid_tuple in \
                    job_metadata[job_name]['nodes-pids'] if
                    node_pid_tuple in all_pids]
                pool.map(self._execute_in_parallel, all_running_jobs)
                print("waiting for other results if any...")

            print("All of the remote results collected.")

    def set_param(self, target, name, parameter, value):
        """
        Used to set a specific parameter in the configuration

        :param target: the entity type on which the parameter is going to be set, e.g. runtime-config
        :param name: the entity name on which the parameter is going to be set, e.g. test-config32
        :param parameter: name of the parameter to be set
        :param value: value of that parameter to be set
        :return:
        """
        if target == 'virtual-cluster':
            self.vcluster_config.deep_set(['virtual-cluster', name, parameter],
                                          value)
            print("Virtual-cluster parameter {} set to {} successfully.".format(
                parameter, value))
        elif target == 'runtime-config':
            self.vcluster_config.deep_set(['runtime-config', name, parameter],
                                          value)
            print(
                "Runtime-configuration parameter {} set to {} successfully.".format(
                    parameter, value))
        else:
            raise ValueError("Target of variable set not found.")

# def main():
#    """
#    Main function for the SSH. Processes the input arguments.
#
#
#    """
#    arguments = docopt(__doc__, version='Cloudmesh virtualcluster 0.1')
#    process_arguments(arguments)
#
#
# if __name__ == "__main__":
#    main()
