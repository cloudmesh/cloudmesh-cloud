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
class Queue(object):

    def __init__(self):
        """
        Initializes the Queue class

        """

        self.cm_config = Config()
        self.queue = {
            'uid': None,
            'queue_name' : None,
            'cluster_name': None,
            'policy': None,
            'status': None,
            'active': None,
            'charge': None,
            'unit': None,
        }
        self.database = CmDatabase()

    @DatabaseUpdate()
    def create(self,
               queue_name,
               cluster_name,
               policy,
               charge = None,
               unit = None):

        """
        This method is used to create a job for running on remote slurm cluster

        :param queue_name: name of the queue to create
        :param cluster_name: slurm cluster on which the job is gonna run
        :return:
        """
        name = Name(
            order=["cloud","name"], cloud=cluster_name, name=queue_name)
        uid = name.id(cloud=cluster_name, name=queue_name)
        print(uid)

        self.queue = {
            'uid': uid,
            "cloud": cluster_name,
            "kind": "batch-queue",
            "name": queue_name,
            "cm": {
                "cloud": cluster_name,
                "kind": "batch-queue",
                "name": queue_name,
                "cluster": self.cm_config.get('cloudmesh').get('cluster')[
                    cluster_name]
            },
            "queue": {
                'policy': policy,
                'status': 'Empty',
                'active': False,
                'charge': charge,
                'unit': unit,
                "numJobs": 0,
                "numRunningJobs": 0,
            }
        }
        if self.database.exists(self.queue)[0]:
            Console.error("Queue already exists")
            return
        return [self.queue]

    def push(self,job):
        '''
        push job to stack
        :param job:
        :return:
        '''
        return

    def pop(self,job):
        '''
        pop job from stack based on the policy
        :param job:
        :return:
        '''
        policy_mapping = {
            'FIFO': self.popFIFO,
            'FILO': self.popFILO
        }

        return

    def popFIFO(self,job):
        '''
        pop job from stack based on FIFO policy
        :param job:
        :return:
        '''
        return

    def popFILO(self, job):
        '''
        pop job from stack based on FIFO policy
        :param job:
        :return:
        '''
        return

    def isEmpty(self):
        '''
        checks if the queue is empty
        :return:
        '''
        return

    def activate(self):
        '''
        activates the queue

        :return:
        '''
        return

    def deactivate(self):
        '''
        deactivates the queue
        :return:
        '''
        return
        

    # the followings are gonna be used:

    # @staticmethod
    # def _execute_in_parallel(func_args):
    #     """
    #     This is a method used for running methods in parallel
    #
    #     :param func_args:
    #     :return:
    #     """
    #     target_class = func_args[0]
    #     method_to_call = getattr(target_class, func_args[1])
    #     args = list(func_args[2:])
    #     return method_to_call(*args)
    #
    # def _fetch_results_in_parallel(self, job_metadata, job_id, all_job_ids):
    #     """
    #     This method is used to fetch the results from remote nodes.
    #
    #     :param job_metadata: the dictionary containing the information about the previously submitted job
    #     :param job_id: the tuple containing destination node, destination pid and destination node index when the job was submitted
    #     :param all_job_ids:
    #     :return:
    #     """
    #     dest_node_info = self.slurm_cluster
    #     path = path_expand(dest_node_info['credentials']['sshconfigpath'])
    #     dest_job_id = job_id
    #     ssh_caller = lambda *x: self._ssh(dest_node_info['name'], path, *x)
    #     scp_caller = lambda *x: self._scp(dest_node_info['name'], path, *x)
    #     #
    #     # use the qstat from cloudmesh, we have a whole library for that
    #     #
    #     ps_output = ssh_caller("qstat -u $USER | grep %s" % job_id)
    #     if len(ps_output) == 0 or ' c ' in ps_output.lower():
    #
    #         if not os.path.exists(job_metadata['local_path']):
    #             os.makedirs(job_metadata['local_path'])
    #         # TODO: REPLACE WITH .format
    #         scp_caller('-r', '%s:%s' % (dest_node_info['name'], job_metadata['remote_path']),
    #                    os.path.join(job_metadata['local_path'], ''))
    #         os.remove(os.path.join(job_metadata['local_path'],
    #                                os.path.basename(os.path.normpath(job_metadata['remote_path'])),
    #                                job_metadata['script_name']))
    #         os.remove(os.path.join(job_metadata['local_path'],
    #                                os.path.basename(os.path.normpath(job_metadata['remote_path'])),
    #                                job_metadata['slurm_script_name']))
    #         if job_metadata['input_type'] == 'params+file':
    #             os.remove(os.path.join(job_metadata['local_path'],
    #                                    os.path.basename(os.path.normpath(job_metadata['remote_path'])),
    #                                    job_metadata['argfile_name']))
    #         all_job_ids.remove(dest_job_id)
    #         # TODO: REPLACE WITH .format
    #         print("Results collected from %s for jobID %s" % (dest_node_info['name'], dest_job_id))
    #
    # @staticmethod
    # def _ssh(hostname, sshconfigpath, *args):
    #     """
    #     This method is used to create remove ssh connections
    #
    #     :param hostname: hostname
    #     :param sshconfigpath: path to sshconfig for connecting to remote node
    #     :param args: the argument to be submitted via ssh
    #     :return:
    #     """
    #     hide_errors_flag = False
    #     if type(args[-1]) == bool:
    #         hide_errors_flag = True
    #         args = args[:-1]
    #     #
    #     # should we use cloudmesh.common.Shell
    #     # shoudl we have a better version of that
    #     #
    #     # (stdout, stderr) = SimpleShell(...)
    #     #
    #     ssh = subprocess.Popen(["ssh", hostname, '-F', sshconfigpath, *args],
    #                            stdout=subprocess.PIPE,
    #                            stderr=subprocess.PIPE)
    #     result = ssh.stdout.readline()
    #     if not result:
    #         error = ssh.stderr.readlines()
    #         if len(error) > 0 and hide_errors_flag == False:
    #             # TODO: REPLACE WITH .format
    #             print("ERROR in host %s: %s" % (hostname, error))
    #         return []
    #     else:
    #         try:
    #             return ''.join([chr(x) for x in result])
    #         except AttributeError:
    #             return [result.decode('utf-8').strip('\n')]
    #
    # @staticmethod
    # def _scp(hostname, sshconfigpath, *args):
    #     """
    #     This method is used for scp from and to remote
    #
    #     :param hostname: hostname
    #     :param sshconfigpath: ssh config file
    #     :param args:arguments for using while copying
    #     :return:
    #     """
    #     ssh = subprocess.Popen(["scp", '-F', sshconfigpath, *args],
    #                            stdout=subprocess.PIPE,
    #                            stderr=subprocess.PIPE)
    #     middle_result = ssh.stdout.readlines()
    #     if not middle_result:
    #         error = ssh.stderr.readlines()
    #         if len(error) > 0:
    #
    #             print("ERROR in host %s: %s" % (hostname, error))
    #
    # @staticmethod
    # def add_suffix_to_path(path, suffix):
    #     """
    #     This method is used to add suffix to a path
    #
    #     :param path: path
    #     :param suffix: suffix
    #     :return:
    #     """
    #     dir_path = os.path.dirname(path)
    #     full_filename = os.path.basename(path)
    #     filename, fileextention = os.path.splitext(full_filename)
    #     full_filename_new = filename + suffix + fileextention
    #     new_path = os.path.join(dir_path, full_filename_new)
    #     return new_path
    #
    # def connection_test(self, slurm_cluster_name):
    #     """
    #     This method is used for testing the connection to the slurm cluster connection node
    #
    #     :param slurm_cluster_name: name of the slurm cluster which is going to be tested
    #     :return:
    #     """
    #     r = self.database.find_name("job_20190327_22265228")
    #     print(r)
    #     return
    #     target_node_info = self.batch_config.get('slurm_cluster')[slurm_cluster_name]
    #     ssh_caller = lambda *x: self._ssh(target_node_info['name'], os.path.expanduser(target_node_info['credentials'] \
    #                                                                                        ['sshconfigpath']), *x)
    #     if len(ssh_caller('uname -a')) > 0:
    #         print("Slurm Cluster {} is accessible.".format(target_node_info['name']))
    #     else:
    #         print("Error: Slurm Cluster {} cannot be accessed.".format(target_node_info['name']))
    #
    # def remove(self, target, key):
    #     """
    #     Used to remove virtual clusters and runtime configs
    #
    #     :param target: type of entity to be removed
    #     :param key: keyname of the entity to be removed
    #     :return:
    #     """
    #     if target == 'slurm-cluster':
    #         self.batch_config.remove(['slurm_cluster'], key)
    #         print("Slurm-cluster {} removed successfully.".format(key))
    #     elif target == 'job':
    #         self.batch_config.remove(['job-metadata'], key)
    #         print("Job {} removed successfully.".format(key))
    #     else:
    #         raise ValueError("Target to remove not found.")
    #
    # def fetch(self, job_name):
    #     """
    #     This method is used to fetch results from remote nodes
    #
    #     :param job_name: the previously submitted job name
    #     :return:
    #     """
    #     job_metadata = self.batch_config.get('job-metadata')[job_name]
    #     self.slurm_cluster = self.batch_config.get('slurm_cluster')[job_metadata['slurm_cluster_name']]
    #     loaded_all_job_ids = [x for x in job_metadata['jobIDs']]
    #     all_job_ids = Manager().list()
    #     all_job_ids.extend(loaded_all_job_ids)
    #     pool = Pool(processes=1)
    #     print("collecting results")
    #     while len(all_job_ids) > 0:
    #         time.sleep(1)
    #         all_running_jobs = [(self, '_fetch_results_in_parallel', job_metadata, jobID, all_job_ids) for \
    #                             jobID in loaded_all_job_ids if jobID in all_job_ids]
    #         pool.map(self._execute_in_parallel, all_running_jobs)
    #         print("waiting for other results if any...")
    #     print("All of the remote results collected.")
    #
    #
    # def set_param(self, target, name, parameter, value):
    #     """
    #     Used to set a specific parameter in the configuration
    #
    #     :param target: the entity type on which the parameter is going to be set, e.g. runtime-config
    #     :param name: the entity name on which the parameter is going to be set, e.g. test-config32
    #     :param parameter: name of the parameter to be set
    #     :param value: value of that parameter to be set
    #     :return:
    #     """
    #     # TODO: .format see if .format(**local) works
    #     if target == 'slurm-cluster':
    #         self.batch_config.deep_set(['slurm_cluster', name, parameter], value)
    #         print("slurm-cluster parameter {} set to {} successfully.".format(parameter, value))
    #     elif target == 'job-metadata':
    #         self.batch_config.deep_set(['job-metadata', name, parameter], value)
    #         print("Job-metadata parameter {} set to {} successfully.".format(parameter, value))
    #     else:
    #         raise ValueError("Target of variable set not found.")