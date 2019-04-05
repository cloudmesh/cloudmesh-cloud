from multiprocessing import Pool, Manager
import subprocess
import os
import ntpath
import time
from pathlib import Path
from pprint import pprint
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.generic_config import GenericConfig
from cloudmesh.common.util import path_expand
from cloudmesh.mongo.DataBaseDecorator import DatabaseUpdate
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.management.configuration.name import Name
from cloudmesh.common.console import Console

from cloudmesh.management.configuration.counter import Counter

# noinspection PyPep8
class SlurmCluster(object):

    def __init__(self):
        """
        Initializes the SlurmCluster class

        """
        # current_path = os.path.dirname(os.path.realpath(__file__))
        # self.workspace = os.path.join(current_path, "batch_workspace/slurm_batch.yaml")
        # if not os.path.exists(os.path.dirname(self.workspace)):
        #     os.makedirs(os.path.dirname(self.workspace))
        self.cm_config = Config()
        # self.batch_config = GenericConfig(self.workspace)
        self.all_jobIDs = []
        self.slurm_cluster = {}
        self.job = {
            'job_name' : None,
            'cluster_name': None,
            'script_path': None,
            'executable_path': None,
            'destination': None,
            'source': None,
            'experiment_name': None,
            'companion_file': None,
        }
        self.database = CmDatabase()

    @staticmethod
    def job_specification():

        # self.job_validator()

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
        }

        return data

    # @DatabaseUpdate
    # def status(self,job_name):
    #     return {
    #         "cloud": self.job.cluster_name,
    #
    #     }


    # noinspection PyDictCreation
    @DatabaseUpdate()
    def create(self,
               job_name,
               cluster_name,
               script_path,
               executable_path,
               destination,
               source,
               experiment_name,
               companion_file):
        """
        This method is used to create a job for running on remote slurm cluster

        :param job_name: name of the job to create
        :param cluster_name: slurm cluster on which the job is gonna run
        :param script_path: path of the slurm script
        :param executable_path: path of the executable that is going to be
        run on the cluster via slurm script
        :param destination: path in the remotes on which the scripts is
        gonna be copied to and ran from
        :param source: local path to which the results are gonna be copied
        :param experiment_name: experiment name and suffix of the filenames in
        the job
        :param companion_file: path of the file that has to be passed to the
        file as an argument if any
        :param overwrite: if the job already exists, this flag overwrites
        the previous job with the same name
        :return:
        """
        # if self.batch_config.get('job-metadata') is not None and job_name in \
        #         list(self.batch_config.get('job-metadata').keys()) and overwrite is False:
        #     raise RuntimeError("The job {} exists in the configuration file, if you want to overwrite the job, \
        #     use --overwrite argument.".format(job_name))

        # tmp_cluster = {cluster_name: dict(slurm_cluster)}
        # slurm_cluster = self.cm_config.get('cloudmesh').get('cluster')[cluster_name]
        # self.batch_config.deep_set(['slurm_cluster'], tmp_cluster)
        name = Name(order=["name","experiment_name"],
                    name=job_name,
                    experiment_name=experiment_name)
        uid = name.id(name=job_name, experiment_name=experiment_name)
        print(uid)
        # return
        # TODO: remove cloud and kind after fixing CmDatabased update
        self.job = {
            'uid': uid,
            "cloud": cluster_name,
            "kind": "batch-job",
            "name" :job_name,
            "cm": {
                "cloud": cluster_name,
                "kind": "batch-job",
                "name": job_name,
                "cluster": self.cm_config.get('cloudmesh').get('cluster')[cluster_name]
            },
            "batch": {
                "status": "pending",
                'script_path': script_path.as_posix(),
                'executable_path': executable_path.as_posix(),
                'destination': destination.as_posix(),
                'source': source.as_posix(),
                'experiment_name': experiment_name,
                'companion_file': companion_file.as_posix()
            }
        }

        # self.job = {
        #         "cloud": cluster_name,
        #         "kind": "batch-job",
        #         "name": job_name,
        #         "cluster": self.cm_config.get('cloudmesh').get('cluster')[
        #             cluster_name],
        #         "status": "pending",
        #         'script_path': script_path.as_posix(),
        #         'executable_path': executable_path.as_posix(),
        #         'destination': destination.as_posix(),
        #         'source': source.as_posix(),
        #         'experiment_name': experiment_name,
        #         'companion_file': companion_file.as_posix()
        # }

        # job['destination'] = os.path.join(job['remote_path'], job['script_name'])
        # job['remote_slurm_script_path'] = os.path.join(job['remote_path'], job['slurm_script_name'])

        # job_metadata = {job_name: job}

        # self.batch_config.deep_set(['job-metadata'], job_metadata)

        # data = self.job_specification()
        if self.database.exists(self.job)[0]:
            Console.error("Job already exists")
            return
        return [self.job]

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

    def _fetch_results_in_parallel(self, job_metadata, job_id, all_job_ids):
        """
        This method is used to fetch the results from remote nodes.

        :param job_metadata: the dictionary containing the information about the previously submitted job
        :param job_id: the tuple containing destination node, destination pid and destination node index when the job was submitted
        :param all_job_ids:
        :return:
        """
        dest_node_info = self.slurm_cluster
        path = path_expand(dest_node_info['credentials']['sshconfigpath'])
        dest_job_id = job_id
        ssh_caller = lambda *x: self._ssh(dest_node_info['name'], path, *x)
        scp_caller = lambda *x: self._scp(dest_node_info['name'], path, *x)
        #
        # use the qstat from cloudmesh, we have a whole library for that
        #
        ps_output = ssh_caller("qstat -u $USER | grep %s" % job_id)
        if len(ps_output) == 0 or ' c ' in ps_output.lower():

            if not os.path.exists(job_metadata['local_path']):
                os.makedirs(job_metadata['local_path'])
            # TODO: REPLACE WITH .format
            scp_caller('-r', '%s:%s' % (dest_node_info['name'], job_metadata['remote_path']),
                       os.path.join(job_metadata['local_path'], ''))
            os.remove(os.path.join(job_metadata['local_path'],
                                   os.path.basename(os.path.normpath(job_metadata['remote_path'])),
                                   job_metadata['script_name']))
            os.remove(os.path.join(job_metadata['local_path'],
                                   os.path.basename(os.path.normpath(job_metadata['remote_path'])),
                                   job_metadata['slurm_script_name']))
            if job_metadata['input_type'] == 'params+file':
                os.remove(os.path.join(job_metadata['local_path'],
                                       os.path.basename(os.path.normpath(job_metadata['remote_path'])),
                                       job_metadata['argfile_name']))
            all_job_ids.remove(dest_job_id)
            # TODO: REPLACE WITH .format
            print("Results collected from %s for jobID %s" % (dest_node_info['name'], dest_job_id))

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
        #
        # should we use cloudmesh.common.Shell
        # shoudl we have a better version of that
        #
        # (stdout, stderr) = SimpleShell(...)
        #
        ssh = subprocess.Popen(["ssh", hostname, '-F', sshconfigpath, *args],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readline()
        if not result:
            error = ssh.stderr.readlines()
            if len(error) > 0 and hide_errors_flag == False:
                # TODO: REPLACE WITH .format
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

    def clean_remote(self, job_name):
        """
        This method is used to spawn processes for cleaning the remote nodes

        :param job_name: name of previously submitted job for which the nodes are going to be cleaned
        :return:
        """
        job_metadata = self.batch_config.get('job-metadata')[job_name]
        target_cluster_info = self.batch_config.get('slurm_cluster')[job_metadata['slurm_cluster_name']]
        remote_path = job_metadata['remote_path']

        ssh_caller = lambda *x: self._ssh(target_cluster_info['name'],
                                          os.path.expanduser(target_cluster_info['credentials'] \
                                                                 ['sshconfigpath']), *x, True)
        ssh_caller('rm -rf {}'.format(remote_path))
        if len(ssh_caller('ls {}'.format(remote_path))) == 0:
            print("Job {} cleaned successfully.".format(job_name))
        else:
            print("Error: Job {} could not be cleaned.".format(job_name))

    def connection_test(self, slurm_cluster_name):
        """
        This method is used for testing the connection to the slurm cluster connection node

        :param slurm_cluster_name: name of the slurm cluster which is going to be tested
        :return:
        """
        r = self.database.find_name("job_20190327_22265228")
        print(r)
        return
        target_node_info = self.batch_config.get('slurm_cluster')[slurm_cluster_name]
        ssh_caller = lambda *x: self._ssh(target_node_info['name'], os.path.expanduser(target_node_info['credentials'] \
                                                                                           ['sshconfigpath']), *x)
        if len(ssh_caller('uname -a')) > 0:
            print("Slurm Cluster {} is accessible.".format(target_node_info['name']))
        else:
            print("Error: Slurm Cluster {} cannot be accessed.".format(target_node_info['name']))

    def remove(self, target, key):
        """
        Used to remove virtual clusters and runtime configs

        :param target: type of entity to be removed
        :param key: keyname of the entity to be removed
        :return:
        """
        if target == 'slurm-cluster':
            self.batch_config.remove(['slurm_cluster'], key)
            print("Slurm-cluster {} removed successfully.".format(key))
        elif target == 'job':
            self.batch_config.remove(['job-metadata'], key)
            print("Job {} removed successfully.".format(key))
        else:
            raise ValueError("Target to remove not found.")

    def fetch(self, job_name):
        """
        This method is used to fetch results from remote nodes

        :param job_name: the previously submitted job name
        :return:
        """
        job_metadata = self.batch_config.get('job-metadata')[job_name]
        self.slurm_cluster = self.batch_config.get('slurm_cluster')[job_metadata['slurm_cluster_name']]
        loaded_all_job_ids = [x for x in job_metadata['jobIDs']]
        all_job_ids = Manager().list()
        all_job_ids.extend(loaded_all_job_ids)
        pool = Pool(processes=1)
        print("collecting results")
        while len(all_job_ids) > 0:
            time.sleep(1)
            all_running_jobs = [(self, '_fetch_results_in_parallel', job_metadata, jobID, all_job_ids) for \
                                jobID in loaded_all_job_ids if jobID in all_job_ids]
            pool.map(self._execute_in_parallel, all_running_jobs)
            print("waiting for other results if any...")
        print("All of the remote results collected.")

    '''
    @DatabaseUpdate
    def list(self, target, max_depth, current_depth=1, input_dict=None):
        """
        listing the target slurm clusters or job-metadata

        :param target: name of the virtual cluster to be listed
        :param max_depth: depth of information to be shown
        :param current_depth: current depth of printing information
        :param input_dict: used for recursion for depth of higher than 1
        :return:
        """
        if target == 'slurm-clusters' and input_dict is None:
            input_dict = self.batch_config.get('slurm_cluster')
        if target == 'jobs' and input_dict is None:
            input_dict = self.batch_config.get('job-metadata')
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
                            self.list(target, max_depth, input_dict=input_dict[key][value],
                                      current_depth=current_depth + 1)
            else:
                indent = current_depth if current_depth > 1 else current_depth - 1
                print('\t' * indent, input_dict)

        data = [{}, {}]
        return data
    '''

    def run(self, job_name):
        """
        This method is used to create a job, validate it and run it on remote nodes

        :param job_name: name of the job to create
        :return:
        """
        job_metadata = self.batch_config.get('job-metadata')[job_name]
        all_job_ids = Manager().list()
        cluster_name = job_metadata['slurm_cluster_name']
        slurm_cluster = self.batch_config.get('slurm_cluster').get(cluster_name)
        path = path_expand(slurm_cluster['credentials']['sshconfigpath'])

        ssh_caller = lambda *x: self._ssh(slurm_cluster['name'], path, *x)
        scp_caller = lambda *x: self._scp(slurm_cluster['name'], path, *x)


        # TODO replace with .format
        ssh_caller('cd %s && mkdir job%s' % (job_metadata['raw_remote_path'], job_metadata['suffix']), True)
        scp_caller(job_metadata['slurm_script_path'],
                   '%s:%s' % (slurm_cluster['name'], job_metadata['remote_slurm_script_path']))
        scp_caller(job_metadata['job_script_path'],
                   '%s:%s' % (slurm_cluster['name'], job_metadata['remote_script_path']))
        ssh_caller('chmod +x', job_metadata['remote_script_path'])
        if job_metadata['input_type'].lower() == 'params+file':
            scp_caller(job_metadata['argfile_path'], '%s:%s' % (slurm_cluster['name'], job_metadata['remote_path']))

        remote_job_id = ssh_caller("cd %s && qsub %s && qstat -u $USER | tail -n 1 | awk '{print $1}'" %
                                   (job_metadata['remote_path'], job_metadata['remote_slurm_script_path']))
        remote_job_id = remote_job_id.strip('\n')
        all_job_ids.append(remote_job_id)
        print('Remote job ID: %s' % remote_job_id)
        self.batch_config.deep_set(['job-metadata', job_name, 'jobIDs'], [pid for pid in all_job_ids])

    def set_param(self, target, name, parameter, value):
        """
        Used to set a specific parameter in the configuration

        :param target: the entity type on which the parameter is going to be set, e.g. runtime-config
        :param name: the entity name on which the parameter is going to be set, e.g. test-config32
        :param parameter: name of the parameter to be set
        :param value: value of that parameter to be set
        :return:
        """
        # TODO: .format see if .format(**local) works
        if target == 'slurm-cluster':
            self.batch_config.deep_set(['slurm_cluster', name, parameter], value)
            print("slurm-cluster parameter {} set to {} successfully.".format(parameter, value))
        elif target == 'job-metadata':
            self.batch_config.deep_set(['job-metadata', name, parameter], value)
            print("Job-metadata parameter {} set to {} successfully.".format(parameter, value))
        else:
            raise ValueError("Target of variable set not found.")


    # def job_validator(self):
    #     """
    #     Used to validate the job-related parameters. If not all of them are
    #     met, then the user will be informed about the missing parameter.
    #
    #     :return: Boolean
    #     """
    #     # job = {
    #     #     'suffix': suffix,
    #     #     'slurm_cluster_name': slurm_cluster_name,
    #     #     'input_type': input_type,
    #     #     'raw_remote_path': remote_path,
    #     #     'slurm_script_path': os.path.abspath(slurm_script_path),
    #     #     'job_script_path': os.path.abspath(job_script_path),
    #     #     'argfile_path': os.path.abspath(argfile_path),
    #     #     'argfile_name': ntpath.basename(argfile_path),
    #     #     'script_name': ntpath.basename(job_script_path),
    #     #     'remote_path': os.path.join(remote_path, 'job' + suffix),
    #     #     'local_path': local_path
    #     # }
    #
    #     mandatory_params = ['slurm_cluster_name', 'input_type',
    #                       'slurm_jobfile_path','binary_path','datafile_path',
    #                       "remote_path",'local_path']
    #     missing_param = None
    #     if self.job['slurm_cluster_name'] is None:
    #         missing_param = 'slurm_cluster_name'
    #         print ("Slurm cluster name not defiend. ")
    #
    #
    #     if missing_param is not None:
    #         print("Set {} using the following command:".format(missing_param))
    #         print("\t cms batch {} set {} {}".format(self.job['jobname'],
    #                                                  missing_param,
    #                                                       missing_param.upper()))
    #         return
    #
    #     # assert input_type in ['params', 'params+file'], "Input type can be either params or params+file"
    #     # if input_type == 'params+file':
    #     #     assert arguments.get("--argfile-path") is not None, "Input type is params+file but the input \
    #     #         filename is not specified"
