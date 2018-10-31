#!/usr/bin/env python3

"""SSH: running parallel remote jobs

Usage:
  VirtualCluster.py vcluster create virtual-cluster <virtualcluster-name> --clusters=<clusterList> [--computers=<computerList>] [--debug]
  VirtualCluster.py vcluster destroy virtual-cluster <virtualcluster-name>
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params out:stdout [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params out:file [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params+file out:stdout [--download-proc-num=<download-pnum> [default=1]]  [--download-now [default=True]]  [--debug]
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params+file out:file [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params+file out:stdout+file [--download-proc-num=<download-pnum> [default=1]] [--download-now [default=True]]  [--debug]
  VirtualCluster.py vcluster set-param runtime-config <config-name> <parameter> <value>
  VirtualCluster.py vcluster destroy runtime-config <config-name>
  VirtualCluster.py vcluster list virtual-clusters [<depth> [default:1]]
  VirtualCluster.py vcluster list runtime-configs [<depth> [default:1]]
  VirtualCluster.py vcluster run-script <job-name> <virtualcluster-name> <config-name> <script-path> <set-of-params-list> <remote-path> <save-to> [--argfile-path=<argfile-path>] [--outfile-name=<outfile-name>] [--suffix=<suffix>] [--overwrite]
  VirtualCluster.py vcluster fetch <job-name>
  VirtualCluster.py vcluster clean-remote <job-name> <proc-num>
  VirtualCluster.py vcluster test-connection <virtualcluster-name> <proc-num>
  VirtualCluster.py -h

Options:
  -h --help     Show this screen.
  --node_list=<list_of_nodes>           List of nodes separated by commas. Ex: node-1,node-2
  --cluster_list=<list_of_clusters>     List of clusters separated by commas. Ex: cluster-1, cluster-2
  --params=<set-of-paramList>           This is a set of parameter list each set is sent to one node. Delimiter for each node is ",", e.g. with 1 2, 3 4, 5 6 the 1 2 will be sent to node1, 3 4 run on node 2, etc.

Description:
   put a description here

Example:
   put an example here
"""

from multiprocessing import Pool, Manager
import subprocess
import os
import ntpath
import time
import pickle
from docopt import docopt
import hostlist
from time import sleep
from datetime import datetime
from cm4.configuration.config import Config
from cm4.configuration.generic_config import GenericConfig
from cm4.abstractclass.CloudManagerABC import CloudManagerABC


class VirtualCluster(object):

    def __init__(self, debug = True):
        """
        Initialize the instance of ssh class
        :param config_path:
        :param output_suffix:
        :param metarun:
        :param debug:
        """
        self.workspace = "./vcluster_workspace/vcluster.yaml"
        if not os.path.exists(os.path.dirname(self.workspace)):
            os.makedirs(os.path.dirname(self.workspace))
        self.cm_config = Config()
        self.vcluster_config = GenericConfig(self.workspace)
        self.debug = debug
        self.all_pids = []

    def fetch(self, job_name):
        job_metadata = self.vcluster_config.get('job-metadata')[job_name]
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[job_metadata['cluster_name']]
        self.runtime_config = self.vcluster_config.get('runtime-config')[job_metadata['config_name']]
        loaded_all_pids =[tuple(x) for x in job_metadata['nodes-pids']]
        all_pids = Manager().list()
        all_pids.extend(loaded_all_pids)
        pool = Pool(processes=self.runtime_config['download_proc_num'])
        print("collecting results")
        while len(all_pids)> 0 :
            time.sleep(1)
            all_running_jobs = [(self,'collect_result',job_metadata, node_pid_tuple, all_pids) for node_pid_tuple in loaded_all_pids if node_pid_tuple in all_pids]
            pool.map(self.run_method_in_parallel, all_running_jobs)
            print ("waiting for other results if any...")
        print("All of the remote results collected.")


    def run(self,job_name, cluster_name,config_name,script_path,argfile_path,outfile_name,remote_path,local_path,params_list,suffix,overwrite):
        if params_list is None:
            raise ValueError('param-list is not set. This value determines how many instance of the target application will run remotely. Therefore, even if the parameter is empty, add commas for every run you expect.')
        if job_name in list(self.vcluster_config.get('job-metadata').keys()) and overwrite is False:
            raise RuntimeError("The job {} exists in the configuration file, if you want to overwrite the job, use --overwrite argument.".format(job_name))
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[cluster_name]
        self.runtime_config = self.vcluster_config.get('runtime-config')[config_name]
        job_metadata = {job_name:{}}
        job_metadata[job_name]['suffix'] = suffix
        job_metadata[job_name]['cluster_name'] = cluster_name
        job_metadata[job_name]['config_name'] = config_name
        job_metadata[job_name]['raw_remote_path'] = remote_path
        job_metadata[job_name]['script_path'] = os.path.abspath(script_path)
        job_metadata[job_name]['argfile_path'] = argfile_path
        job_metadata[job_name]['argfile_name'] = ntpath.basename(argfile_path)
        if len(job_metadata[job_name]['argfile_name']) > 0:
            job_metadata[job_name]['params_list'] = ['{} {}'.format(job_metadata[job_name]['argfile_name'],x) for x in params_list]
        else:
            job_metadata[job_name]['params_list'] = params_list

        job_metadata[job_name]['outfile_name'] = outfile_name
        job_metadata[job_name]['script_name'] = ntpath.basename(script_path)
        job_metadata[job_name]['script_name_with_suffix'] = self.add_suffix_to_path(job_metadata[job_name]['script_name'],suffix)
        job_metadata[job_name]['remote_path'] = os.path.join(remote_path,'job' + suffix,'')
        job_metadata[job_name]['remote_script_path'] = os.path.join(job_metadata[job_name]['remote_path'], job_metadata[job_name]['script_name_with_suffix'])
        job_metadata[job_name]['local_path'] = local_path

        self.job_metadata = job_metadata
        self.vcluster_config.deep_set(['job-metadata'], job_metadata)
        all_pids = Manager().list()
        all_jobs = [(self,'run_remote_job',job_metadata[job_name],param_idx, param, all_pids) for param_idx,param in enumerate(job_metadata[job_name]['params_list'])]
        pool = Pool(processes=self.runtime_config['proc_num'])
        pool.map(self.run_method_in_parallel,all_jobs)
        self.all_pids = all_pids
        self.vcluster_config.deep_set(['job-metadata',job_name,'nodes-pids' ],all_pids._getvalue())
        if self.runtime_config['download-now']:
            # parallel_jobs.sync_pids_with_config()
            pool = Pool(processes=self.runtime_config['download_proc_num'])
            print("collecting results")
            while len(all_pids)> 0 :
                time.sleep(3)
                all_running_jobs = [(self,'collect_result',job_metadata[job_name], node_pid_tuple, all_pids) for node_pid_tuple in job_metadata[job_name]['nodes-pids'] if node_pid_tuple in all_pids]
                pool.map(self.run_method_in_parallel, all_running_jobs)
                print ("waiting for other results if any...")

            print("All of the remote results collected.")

    def collect(self):
        pass


    def collect_result(self,job_metadata,  node_pid_tuple,all_pids):
        dest_node = node_pid_tuple[0]
        dest_pid = node_pid_tuple[1]
        node_idx = node_pid_tuple[2]
        dest_node_info = self.virt_cluster[dest_node]
        ssh_caller = lambda *x: self.ssh(dest_node_info['name'],os.path.expanduser(dest_node_info['credentials']['sshconfigpath']),*x)
        scp_caller = lambda *x: self.scp(dest_node_info['name'],os.path.expanduser(dest_node_info['credentials']['sshconfigpath']),*x)
        ps_output = ssh_caller('ps', '-ef', '|', 'grep', dest_pid, '|', 'grep -v grep')
        if len(ps_output) == 0 and node_pid_tuple in all_pids._getvalue():
            if not os.path.exists(job_metadata['local_path']):
                os.makedirs(job_metadata['local_path'])
            if self.runtime_config['output-type'] == 'stdout':
                scp_caller('%s:%s' % (dest_node_info['name'], os.path.join(job_metadata['remote_path'],self.add_suffix_to_path('outputfile_%d' % node_idx, job_metadata['suffix']))),os.path.join(job_metadata['local_path'], ''))
            elif self.runtime_config['output-type'] in  ['file' , 'stdout+file'] :
                nested_remote_path = os.path.join(job_metadata['remote_path'], 'run{}'.format(node_idx))
                scp_caller('-r', '%s:%s' % (dest_node_info['name'], nested_remote_path),os.path.join(job_metadata['local_path'], ''))
            all_pids.remove((dest_node, dest_pid,node_idx))
            print("Results collected from %s."%dest_node)

    def run_remote_job(self, job_metadata, param_idx, params, all_pids):
        ## COPY SCRIPT TO REMOTE
        available_nodes_num =  len(list(self.virt_cluster.keys()))
        target_node_idx = param_idx%available_nodes_num
        target_node_key = list(self.virt_cluster.keys())[target_node_idx]
        target_node = self.virt_cluster[target_node_key]
        ssh_caller = lambda *x: self.ssh(target_node['name'],os.path.expanduser(target_node['credentials']['sshconfigpath']),*x)
        scp_caller = lambda *x: self.scp(target_node['name'],os.path.expanduser(target_node['credentials']['sshconfigpath']),*x)
        if len(ssh_caller('if test -d %s; then echo "exist"; fi'%job_metadata['remote_path'])) == 0:
            ssh_caller('cd %s && mkdir job%s'%(job_metadata['raw_remote_path'],job_metadata['suffix']))
        if self.runtime_config['output-type'].lower() in ['file','stdout+file']:
            ssh_caller("cd {} && mkdir run{}".format(job_metadata['remote_path'],param_idx))
            nested_remote_path = os.path.join(job_metadata['remote_path'],'run{}'.format(param_idx),job_metadata['script_name_with_suffix'])
            scp_caller(job_metadata['script_path'], '%s:%s' % (target_node['name'], nested_remote_path))
            ssh_caller('chmod +x', nested_remote_path)
            if self.runtime_config['input-type'].lower() == 'params+file':
                scp_caller(job_metadata['argfile_path'],'%s:%s' % (target_node['name'], os.path.join(job_metadata['remote_path'],'run{}'.format(param_idx),job_metadata['argfile_name'])))
        else:
            scp_caller(job_metadata['script_path'],'%s:%s' % (target_node['name'], job_metadata['remote_script_path']))
            ssh_caller('chmod +x', job_metadata['remote_script_path'])
            if self.runtime_config['input-type'].lower() == 'params+file':
                scp_caller(job_metadata['argfile_path'],'%s:%s' % (target_node['name'], job_metadata['remote_path']))

        if self.runtime_config['output-type'].lower() == 'stdout':
            remote_pid = ssh_caller('cd %s && nohup %s %s > %s 2>&1 </dev/null& echo $!' % (job_metadata['remote_path'], job_metadata['remote_script_path'], params, os.path.join(job_metadata['remote_path'], self.add_suffix_to_path('outputfile_%d' % param_idx, job_metadata['suffix']))))
        elif self.runtime_config['output-type'].lower() == 'stdout+file':
            remote_pid = ssh_caller('cd %s && nohup %s %s > %s 2>&1 </dev/null& echo $!' % (os.path.join(job_metadata['remote_path'],'run{}'.format(param_idx)), os.path.join(job_metadata['remote_path'],'run{}'.format(param_idx),job_metadata['script_name_with_suffix']), params,os.path.join(job_metadata['remote_path'], 'run{}'.format(param_idx),self.add_suffix_to_path('outputfile_%d' % param_idx, job_metadata['suffix']))))
        elif self.runtime_config['output-type'].lower() == 'file':
            remote_pid = ssh_caller('cd %s && nohup ./%s %s >&- & echo $!' % (os.path.join(job_metadata['remote_path'],'run{}'.format(param_idx)), job_metadata['script_name_with_suffix'], params))
        all_pids.append((target_node_key,remote_pid[0],param_idx))
        print('Remote Pid on %s: %s'%(target_node_key,remote_pid[0]))


    def ssh(self,hostname, sshconfigpath, *args):
        ssh = subprocess.Popen(["ssh", hostname , '-F', sshconfigpath, *args ],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readline()
        if result == []:
            error = ssh.stderr.readlines()
            if len(error) > 0:
                print("ERROR in host %s: %s" % (hostname,error))
            return []
        else:
            try:
                return [x.decode('utf-8').strip('\n') for x in result]
            except AttributeError:
                return [result.decode('utf-8').strip('\n')]

    def scp(self, hostname, sshconfigpath, *args):
        ssh = subprocess.Popen(["scp", '-F', sshconfigpath, *args],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        middle_result = ssh.stdout.readlines()
        if middle_result == []:
            error = ssh.stderr.readlines()
            if len(error) > 0:
                print("ERROR in host %s: %s" % (hostname, error))

    # def config_validator(self,config_path):
    #     self.config_path = config_path
    #     try:
    #         self.config = ConfigObj(self.config_path)
    #     except ConfigObjError:
    #         raise ValueError("Config file cannot be parsed, make sure there is no duplicates in the top level node names")
    #     for n_idx, n in enumerate(self.config):
    #         if 'hostname' not in self.config[n].keys():
    #             raise ValueError("%s: 'hostname' keyword is missing"%n)
    #         if 'sshconfigpath' not in self.config[n].keys():
    #             raise ValueError("%s: 'sshconfigpath' keyword is missing" % n)
    #         if not os.path.isfile(os.path.expanduser(self.config[n]['sshconfigpath'])):
    #             raise ValueError("%s: The ssh config file %s does not exists" % (n,self.config[n]['sshconfigpath']))
    #         if 'script_path' not in self.config[n].keys():
    #             raise ValueError("%s: 'script_path' keyword is missing" % n)
    #         if not os.path.isfile(os.path.expanduser(self.config[n]['script_path'])):
    #             raise ValueError("%s: The script file %s does not exists" % (n, self.config[n]['script_path']))
    #         if 'remote_path' not in self.config[n].keys():
    #             raise ValueError("%s: 'remote_path' keyword is missing" % n)
    #         if 'arg_type' not in self.config[n].keys():
    #             raise ValueError("%s: 'arg_type' keyword is missing" % n)
    #
    #         if self.config[n]['arg_type'] == 'params':
    #             if 'arg_params' not in self.config[n].keys():
    #                 raise ValueError("%s: 'arg_type' is defined as params, but 'arg_params' keyword is missing" % n)
    #         elif self.config[n]['arg_type'] == 'params+file':
    #             if 'arg_params' not in self.config[n].keys():
    #                 raise ValueError("%s: 'arg_type' is defined as params+file, in this case the 'arg_params' is also needed but 'arg_params' keyword is missing" % n)
    #             if 'arg_file_path' not in self.config[n].keys():
    #                 raise ValueError("%s: arg_type is defined as file, but 'arg_file_path' keyword is missing" % n)
    #             if not os.path.isfile(os.path.expanduser(self.config[n]['arg_file_path'])):
    #                 raise ValueError("%s: The arg file %s does not exists" % (n, self.config[n]['arg_file_path']))
    #         if 'output_type' not in self.config[n].keys():
    #             raise ValueError("%s: 'output_type' keyword is missing" % n)
    #         if self.config[n]['output_type'] in ['file' ,'stdout+file'] :
    #             if 'output_filename' not in self.config[n].keys():
    #                 raise ValueError("%s: 'output_type' is defined as file, but 'output_filename' keyword is missing" % n)
    #         if 'local_output_path' not in self.config[n].keys():
    #             raise ValueError("%s: 'local_output_path' keyword is missing" % n)

    def add_suffix_to_path(self,path,suffix):
        dir_path = os.path.dirname(path)
        full_filename = os.path.basename(path)
        filename, fileextention =  os.path.splitext(full_filename)
        full_filename_new = filename + suffix + fileextention
        new_path = os.path.join(dir_path,full_filename_new)
        return new_path

    def build_metadata(self):
        self.metadata = {}
        self.metadata['all_pids'] = self.all_pids._getvalue()
        self.metadata['config'] = self.config
        self.metadata['output_suffix'] = self.output_suffix
        return self.metadata

    def load_metadata(self,input_metadata):
        self.config = input_metadata['config']
        self.all_pids = input_metadata['all_pids']
        self.output_suffix = input_metadata['output_suffix']
        all_pids_dict = dict(self.all_pids)
        for n_idx,n in enumerate(self.config):
            self.config[n]['pid'] = all_pids_dict[n]


    def list(self,target,max_depth,current_depth=1,input_dict=None):
        """
        listing the current virtual clusters based on the vcluster_conf file.

        :param max_depth: depth of information to be shown
        :param input_dict: used for recursion for depth of higher than 1
        :param current_depth: current depth of printing information
        :return:
        """
        if target=='virtual-clusters' and input_dict==None:
            input_dict = self.vcluster_config._conf_dict['virtual-cluster']
        elif target == 'runtime-configs'and input_dict==None:
            input_dict = self.vcluster_config._conf_dict['runtime-config']
        elif input_dict==None:
            raise ValueError("Target of listing not found.")

        if max_depth>=current_depth:
            if type(input_dict)==dict:
                for key in input_dict:
                    key_to_print = key + ':' if max_depth>=current_depth else key
                    indent = current_depth if current_depth>1 else current_depth-1
                    print('\t'*indent,key_to_print)
                    if type(input_dict.get(key))!=dict:
                        print('\t' * (indent + 1), input_dict.get(key))
                    else:
                        for value in input_dict.get(key):
                            value_to_print = value + ':' if max_depth > current_depth else value
                            print ('\t'*(indent+1),value_to_print)
                            self.list(target,max_depth,input_dict=input_dict[key][value],current_depth=current_depth+1)
            else:
                indent = current_depth if current_depth > 1 else current_depth - 1
                print('\t' * indent, input_dict)

    def _create_vcluster(self, vcluster_name, cluster_list=[], computer_list=[]):
        vcluster_tosave = {vcluster_name: {}}
        for cluster in cluster_list:
            for computer in self.cm_config.get('cluster.{}'.format(cluster)):
                if computer in computer_list or computer_list == '':
                    vcluster_tosave[vcluster_name].update({computer: dict(self.cm_config.get('cluster.{}.{}'.format(cluster, computer)))})
        self.vcluster_config.deep_set(['virtual-cluster'], vcluster_tosave)
        print("Virtual cluster created/replaced successfully.")

    def _create_config(self,config_name,proc_num,download_proc_num,download_now,save_to,input_type,output_type):
        config_tosave = {config_name:{}}
        config_tosave[config_name].update({"proc_num":proc_num,
                                           "download_proc_num": download_proc_num,
                                           "download-now": download_now,
                                           "save-to":save_to,
                                           "input-type":input_type,
                                           "output-type":output_type})
        self.vcluster_config.deep_set(['runtime-config'],config_tosave)
        print("Runtime-configuration created/replaced successfully.")

    def create(self,*args,**kwargs):
        if len(args) > 5 :
            self._create_config(*args)
        else:
            self._create_vcluster(*args,**kwargs)

    def destroy(self,target, key):
        if target=='virtual-cluster':
            self.vcluster_config.remove(['virtual-cluster'], key)
            print("Virtual-cluster {} destroyed successfully.".format(key))
        elif target == 'runtime-config':
            self.vcluster_config.remove(['runtime-config'], key)
            print("Runtime-configuration {} destroyed successfully.".format(key))
        else:
            raise ValueError("Target of destroying not found.")

    def set_param(self,target,name,parameter,value):
        if target=='virtual-cluster':
            self.vcluster_config.deep_set(['virtual-cluster',name,parameter], value)
            print("Virtual-cluster parameter {} set to {} successfully.".format(parameter,value))
        elif target == 'runtime-config':
            self.vcluster_config.deep_set(['runtime-config',name,parameter],value)
            print("Runtime-configuration parameter {} set to {} successfully.".format(parameter, value))
        else:
            raise ValueError("Target of variable set not found.")

    def run_method_in_parallel(self,func_args):
        target_class = func_args[0]
        method_to_call = getattr(target_class,func_args[1] )
        args = list(func_args[2:])
        return method_to_call(*args)

    def connection_test(self,vcluster_name,proc_num):
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[vcluster_name]
        all_jobs = [(self, 'run_connection_test_parallel' ,node) for node in list(self.virt_cluster)]
        pool = Pool(processes=proc_num)
        pool.map(self.run_method_in_parallel, all_jobs)

    def run_connection_test_parallel(self, target_node):
        target_node_info = self.virt_cluster[target_node]
        ssh_caller = lambda *x: self.ssh(target_node_info['name'],os.path.expanduser(target_node_info['credentials']['sshconfigpath']),*x)
        if len(ssh_caller('uname -a')) > 0:
            print("Node {} is accessible.".format(target_node))
        else:
            print("Error: Node {} cannot be accessed.".format(target_node))

    def clean_remote(self,job_name,proc_num):
        job_metadata = self.vcluster_config.get('job-metadata')[job_name]
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[job_metadata['cluster_name']]
        remote_path = job_metadata['remote_path']
        all_jobs = [(self, 'run_clean_remote_parallel' ,node,remote_path) for node in list(self.virt_cluster)]
        pool = Pool(processes=proc_num)
        pool.map(self.run_method_in_parallel, all_jobs)

    def run_clean_remote_parallel(self, target_node,remote_path):
        target_node_info = self.virt_cluster[target_node]
        ssh_caller = lambda *x: self.ssh(target_node_info['name'],os.path.expanduser(target_node_info['credentials']['sshconfigpath']),*x)
        ssh_caller('rm -rf {}'.format(remote_path))
        if len(ssh_caller('ls {}'.format(remote_path))) == 0:
            print("Node {} cleaned successfully.".format(target_node))
        else:
            print("Error: Node {} could not be cleaned.".format(target_node))



def process_arguments(arguments):
    """
    Processes all the input arguments and acts accordingly.

    :param arguments: input arguments for the virtual cluster script.

    """
    debug = arguments["--debug"]

    if arguments.get("vcluster"):
        vcluster_manager = VirtualCluster(debug=debug)
        if arguments.get("create"):
            if arguments.get("virtual-cluster") and arguments.get("--clusters"):
                clusters = hostlist.expand_hostlist(arguments.get("--clusters"))
                computers = hostlist.expand_hostlist(arguments.get("--computers"))
                vcluster_manager.create(arguments.get("<virtualcluster-name>"),cluster_list=clusters,computer_list=computers)
            elif arguments.get("runtime-config") and arguments.get("<config-name>") and arguments.get("<proc-num>"):
                config_name = arguments.get("<config-name>")
                proc_num = int(arguments.get("<proc-num>"))
                download_proc_num = 1 if arguments.get("<download-pnum>") is None else int(arguments.get("<download-pnum>"))

                save_to = "" if arguments.get("<save-path>") is None else arguments.get("<save-path>")
                download_now = True if arguments.get("--download-now") is False else False
                # if len(params_list) != proc_num:
                #     raise ValueError("There should be one parameter for each remote node so that the runs are not identical and redundant.")
                if arguments.get("in:params") and arguments.get("out:stdout"):
                    input_type = "params"
                    output_type = "stdout"
                elif arguments.get("in:params") and arguments.get("out:file"):
                    input_type = "params"
                    output_type = "file"
                elif arguments.get("in:params+file") and arguments.get("out:stdout"):
                    input_type = "params+file"
                    output_type = "stdout"
                elif arguments.get("in:params+file") and arguments.get("out:file"):
                    input_type = "params+file"
                    output_type = "file"
                elif arguments.get("in:params+file") and arguments.get("out:stdout+file"):
                    input_type = "params+file"
                    output_type = "stdout+file"
                vcluster_manager.create(config_name,proc_num,download_proc_num,download_now,save_to,input_type,output_type)

        elif arguments.get("destroy"):
            if arguments.get("virtual-cluster"):
                vcluster_manager.destroy("virtual-cluster",arguments.get("<virtualcluster-name>"))
            elif arguments.get("runtime-config"):
                vcluster_manager.destroy("runtime-config",arguments.get("<config-name>"))

        elif arguments.get("list"):
            if arguments.get("virtual-clusters"):
                max_depth = 1 if arguments.get("<depth>") is None else int(arguments.get("<depth>"))
                vcluster_manager.list("virtual-clusters",max_depth)
            elif arguments.get("runtime-configs"):
                max_depth = 1 if arguments.get("<depth>") is None else int(arguments.get("<depth>"))
                vcluster_manager.list("runtime-configs",max_depth)

        elif arguments.get("set-param"):
            if arguments.get("virtual-clusters"):
                cluster_name = arguments.get("<virtualcluster-name>")
                parameter = arguments.get("<parameter>")
                value = arguments.get("<value>")
                vcluster_manager.set_param("virtual-clusters",cluster_name,parameter,value)

            if arguments.get("runtime-config"):
                config_name = arguments.get("<config-name>")
                parameter = arguments.get("<parameter>")
                value = arguments.get("<value>")
                vcluster_manager.set_param("runtime-config",config_name,parameter,value)
        elif arguments.get("run-script"):
            job_name = arguments.get("<job-name>")
            cluster_name = arguments.get("<virtualcluster-name>")
            config_name = arguments.get("<config-name>")
            script_path = arguments.get("<script-path>")
            remote_path = arguments.get("<remote-path>")
            local_path = arguments.get("<save-to>")
            random_suffix = '_' + str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '')[
                                  0:str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '').index(
                                      '.') + 3].replace('.', '')
            suffix = random_suffix if arguments.get("suffix") is None else arguments.get("suffix")
            params_list = arguments.get("<set-of-params-list>").split(',')
            overwrite = False if type(arguments.get("--overwrite")) is None else arguments.get("--overwrite")
            argfile_path = '' if arguments.get("--argfile-path") is None else arguments.get("--argfile-path")
            outfile_name = '' if arguments.get("--outfile-name") is None else arguments.get("--outfile-name")
            vcluster_manager.run(job_name,cluster_name,config_name,script_path,argfile_path,outfile_name,remote_path,local_path,params_list,suffix,overwrite)
        elif arguments.get("fetch"):
            job_name = arguments.get("<job-name>")
            vcluster_manager.fetch(job_name)
        elif arguments.get("test-connection"):
            vcluster_name = arguments.get("<virtualcluster-name>")
            proc_num = int(arguments.get("<proc-num>"))
            vcluster_manager.connection_test(vcluster_name,proc_num)
        elif arguments.get("clean-remote"):
            job_name = arguments.get("<job-name>")
            proc_num = int(arguments.get("<proc-num>"))
            vcluster_manager.clean_remote(job_name,proc_num)

def main():
    """
    Main function for the SSH. Processes the input arguments.


    """
    arguments = docopt(__doc__, version='Cloudmesh VirtualCluster 0.1')
    process_arguments(arguments)


if __name__ == "__main__":
    main()
