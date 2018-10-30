#!/usr/bin/env python3

"""SSH: running parallel remote jobs

Usage:
  VirtualCluster.py vcluster create virtual-cluster <virtualcluster-name> --clusters=<clusterList> [--computers=<computerList>] [--debug]
  VirtualCluster.py vcluster destroy virtual-cluster <virtualcluster-name>
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params out:stdout [--download-proc-num=<download-pnum> [default=1]] [--download-now]  [--debug]
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params out:file [--download-proc-num=<download-pnum> [default=1]] [--download-now]  [--debug]
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params+file out:stdout [--download-proc-num=<download-pnum> [default=1]]  [--download-now]  [--debug]
  VirtualCluster.py vcluster create runtime-config <config-name> <proc-num> in:params+file out:file [--download-proc-num=<download-pnum> [default=1]] [--download-now]  [--debug]
  VirtualCluster.py vcluster set-param runtime-config <config-name> <parameter> <value>
  VirtualCluster.py vcluster destroy runtime-config <config-name>
  VirtualCluster.py vcluster list virtual-clusters [<depth> [default:1]]
  VirtualCluster.py vcluster list runtime-configs [<depth> [default:1]]
  VirtualCluster.py vcluster run-script <job-name> <virtualcluster-name> <config-name> <script-path> <remote-path> <save-to> [--argfile-path=<argfile-path>] [--outfile-name=<outfile-name>] [--params=<set-of-params-list>] [--suffix=<suffix>] [--overwrite]
  VirtualCluster.py vcluster connection-test

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

# from configobj import ConfigObj,ConfigObjError
from multiprocessing import Pool, Manager
import subprocess
import os
import ntpath
import time
import argparse
import sys
import pickle
from collections import OrderedDict
from docopt import docopt
from cm4.configuration.dot_dictionary import DotDictionary
import hostlist
import fileinput
from datetime import datetime
from cm4.configuration.config import Config
from cm4.configuration.generic_config import GenericConfig
from cm4.abstractclass.CloudManagerABC import CloudManagerABC


#TODO cleanup remote
#TODO multiple output files

class VirtualCluster(CloudManagerABC):

    def __init__(self, metarun=False, debug = False):
        """
        Initialize the instance of ssh class
        :param config_path:
        :param output_suffix:
        :param metarun:
        :param debug:
        """
        if not metarun:
            self.workspace = "./vcluster_workspace/vcluster.yaml"
            if not os.path.exists(os.path.dirname(self.workspace)):
                os.makedirs(os.path.dirname(self.workspace))
            self.cm_config = Config()
            self.vcluster_config = GenericConfig(self.workspace)

            self.debug = 1
            # self.config_validator(config_path)
            self.all_pids = []
            # self.output_suffix = output_suffix
            # for n_idx, n in enumerate(self.config):
            #     self.config[n]['node'] = n
            #     self.config[n]['node_idx'] = n_idx
            #     self.config[n]['sshconfigpath'] = os.path.expanduser(self.config[n]['sshconfigpath'])
            #     self.config[n]['local_output_path'] = os.path.expanduser(self.config[n]['local_output_path'])
            #     self.config[n]['script_path'] = os.path.expanduser(self.config[n]['script_path'])
            #     self.config[n]['script_name'] = ntpath.basename(self.config[n]['script_path'])
            #     self.config[n]['script_name_with_suffix'] = self.add_suffix_to_path(self.config[n]['script_name'])
            #     self.config[n]['remote_path'] = self.ssh(n, 'cd %s && pwd'% (os.path.join(self.config[n]['remote_path'])))[0]
            #     remote_path_with_suffix_folder = os.path.join(self.config[n]['remote_path'],
            #                                                              'files' + self.output_suffix,'')
            #     if len(self.ssh(n, 'if test -d %s; then echo "exist"; fi'%remote_path_with_suffix_folder)) == 0:
            #         self.ssh(n, 'cd %s && mkdir files%s'%(self.config[n]['remote_path'],self.output_suffix))
            #     self.config[n]['remote_path'] = remote_path_with_suffix_folder
            #     if self.config[n]['arg_type'].lower() == 'file':
            #         self.config[n]['arg_filename'] = os.path.expanduser(ntpath.basename(self.config[n]['arg_file_path']))
            #     self.config[n]['remote_script_path'] = os.path.join(self.config[n]['remote_path'], self.config[n]['script_name_with_suffix'])



    def destroy(self):
        pass
    def info(self):
        pass
    def ls(self):
        pass
    def resume(self):
        pass
    def stop(self):
        pass
    def suspend(self):
        pass
    def start(self):
        pass


    def run(self,job_name, cluster_name,config_name,script_path,argfile_path,outfile_name,remote_path,local_path,params_list,suffix,overwrite):
        if params_list is None:
            raise ValueError('param-list is not set. This value determines how many instance of the target application will run remotely. Therefore, even if the parameter is empty, add commas for every run you expect.')
        if job_name in list(self.vcluster_config.get('job-metadata').keys()) and overwrite is False:
            raise RuntimeError("The job {} exists in the configuration file, if you want to overwrite the job, use --overwrite argument.".format(job_name))
        self.virt_cluster = self.vcluster_config.get('virtual-cluster')[cluster_name]
        self.runtime_config = self.vcluster_config.get('runtime-config')[config_name]
        # job_number = 1 if self.vcluster_config.get('job-metadata') is None else max([int(x.split('-')[1]) for x in self.vcluster_config.get('job-metadata').keys()]) + 1
        job_metadata = {job_name:{}}
        job_metadata[job_name]['suffix'] = suffix
        job_metadata[job_name]['raw_remote_path'] = remote_path
        job_metadata[job_name]['script_path'] = os.path.abspath(script_path)
        job_metadata[job_name]['argfile_path'] = argfile_path
        job_metadata[job_name]['outfile_path'] = outfile_name
        job_metadata[job_name]['script_name'] = ntpath.basename(script_path)
        job_metadata[job_name]['script_name_with_suffix'] = self.add_suffix_to_path(job_metadata[job_name]['script_name'],suffix)
        job_metadata[job_name]['remote_path'] = os.path.join(remote_path,'job' + suffix,'')
        job_metadata[job_name]['remote_script_path'] = os.path.join(job_metadata[job_name]['remote_path'], job_metadata[job_name]['script_name_with_suffix'])
        job_metadata[job_name]['local_path'] = local_path
        job_metadata[job_name]['params_list'] = params_list
        self.job_metadata = job_metadata

        self.vcluster_config.deep_set(['job-metadata'], job_metadata)
        all_pids = Manager().list()
        all_jobs = [(self,job_metadata[job_name],param_idx, param, all_pids) for param_idx,param in enumerate(params_list)]
        pool = Pool(processes=self.runtime_config['proc_num'])
        pool.map(run_method_in_parallel,all_jobs)
        self.all_pids = all_pids
        self.vcluster_config.deep_set(['job-metadata',job_name,'nodes-pids' ],all_pids._getvalue())
        if self.runtime_config['download-now']:
            # parallel_jobs.sync_pids_with_config()
            pool = Pool(processes=self.runtime_config['download_proc_num'])
            print("collecting results")
            while len(all_pids)> 0 :
                time.sleep(3)
                all_running_jobs = [(self,job_metadata[job_name], node_idx,node_pid_tuple, all_pids) for node_idx, node_pid_tuple in enumerate(self.vcluster_config.get('job-metadata')['j1test']['nodes-pids']) if node_pid_tuple in all_pids]
                pool.map(collect_results_in_parallel, all_running_jobs)
                print ("waiting for other results if any...")

            print("All of the remote results collected.")

    def collect(self):
        pass


    def collect_result(self,job_metadata, node_idx, node_pid_tuple,all_pids):
        dest_node = node_pid_tuple[0]
        dest_pid = node_pid_tuple[1]
        dest_node_info = self.virt_cluster[dest_node]
        ssh_caller = lambda *x: self.ssh(dest_node_info['name'],os.path.expanduser(dest_node_info['credentials']['sshconfigpath']),*x)
        scp_caller = lambda *x: self.scp(dest_node_info['name'],os.path.expanduser(dest_node_info['credentials']['sshconfigpath']),*x)
        ps_output = ssh_caller('ps', '-ef', '|', 'grep', dest_pid, '|', 'grep -v grep')
        if len(ps_output) == 0 :
            if not os.path.exists(job_metadata['local_path']):
                os.makedirs(job_metadata['local_path'])
            if self.runtime_config['output-type'] == 'stdout':
                scp_caller('%s:%s' % (dest_node_info['name'], os.path.join(job_metadata['remote_path'],self.add_suffix_to_path('outputfile_%d' % node_idx, job_metadata['suffix']))),os.path.join(job_metadata['local_path'], ''))
            elif self.runtime_config['output-type'] == 'file':
                scp_caller('-r', '%s:%s' % (dest_node_info['name'], os.path.join(job_metadata['remote_path'], job_metadata['outfile_name'])),os.path.join(job_metadata['local_path'], ''))
            elif self.runtime_config['output-type'] == 'stdout+file':
                scp_caller('%s:%s' % (dest_node_info['name'], os.path.join(job_metadata['remote_path'], self.add_suffix_to_path('outputfile_%d' %node_idx,job_metadata['suffix']))), os.path.join(job_metadata['local_path'], ''))
                scp_caller('-r', '%s:%s' % (dest_node_info['name'], os.path.join(job_metadata['remote_path'], job_metadata['outfile_name'])),os.path.join(job_metadata['local_path'], ''))
            all_pids.remove((dest_node, dest_pid))
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
        scp_caller(job_metadata['script_path'],'%s:%s' % (target_node['name'], os.path.join(job_metadata['remote_path'],job_metadata['script_name_with_suffix'])))

        if self.debug:
            print("script copied")

        ssh_caller('chmod +x' , job_metadata['remote_script_path'])

        if self.debug:
            print("chmod +x set")

        ## COPY INPUT TO REMOTE AND RUN
        if self.runtime_config['input-type'].lower() == 'params+file':
            scp_caller(self.runtime_config['infile-path'],'%s:%s' % (target_node['name'], job_metadata['remote_path']))
        if self.runtime_config['output-type'].lower() in ['stdout','stdout+file']:
            remote_pid = ssh_caller('cd %s && nohup %s %s > %s 2>&1 </dev/null& echo $!' % (job_metadata['remote_path'], job_metadata['remote_script_path'], params, os.path.join(job_metadata['remote_path'], self.add_suffix_to_path('outputfile_%d' % param_idx, job_metadata['suffix']))))
            if self.debug:
                print("params->stdout ran")
        elif self.runtime_config['output-type'].lower() == 'file':
            remote_pid = ssh_caller('cd %s && nohup %s %s > &- 2>&1 & echo $!' % (job_metadata['remote_path'], job_metadata['remote_script_path'], params))
            if self.debug:
                print("params->file ran")
        all_pids.append((target_node_key,remote_pid[0]))
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

    def config_validator(self,config_path):
        self.config_path = config_path
        try:
            self.config = ConfigObj(self.config_path)
        except ConfigObjError:
            raise ValueError("Config file cannot be parsed, make sure there is no duplicates in the top level node names")
        for n_idx, n in enumerate(self.config):
            if 'hostname' not in self.config[n].keys():
                raise ValueError("%s: 'hostname' keyword is missing"%n)
            if 'sshconfigpath' not in self.config[n].keys():
                raise ValueError("%s: 'sshconfigpath' keyword is missing" % n)
            if not os.path.isfile(os.path.expanduser(self.config[n]['sshconfigpath'])):
                raise ValueError("%s: The ssh config file %s does not exists" % (n,self.config[n]['sshconfigpath']))
            if 'script_path' not in self.config[n].keys():
                raise ValueError("%s: 'script_path' keyword is missing" % n)
            if not os.path.isfile(os.path.expanduser(self.config[n]['script_path'])):
                raise ValueError("%s: The script file %s does not exists" % (n, self.config[n]['script_path']))
            if 'remote_path' not in self.config[n].keys():
                raise ValueError("%s: 'remote_path' keyword is missing" % n)
            if 'arg_type' not in self.config[n].keys():
                raise ValueError("%s: 'arg_type' keyword is missing" % n)

            if self.config[n]['arg_type'] == 'params':
                if 'arg_params' not in self.config[n].keys():
                    raise ValueError("%s: 'arg_type' is defined as params, but 'arg_params' keyword is missing" % n)
            elif self.config[n]['arg_type'] == 'params+file':
                if 'arg_params' not in self.config[n].keys():
                    raise ValueError("%s: 'arg_type' is defined as params+file, in this case the 'arg_params' is also needed but 'arg_params' keyword is missing" % n)
                if 'arg_file_path' not in self.config[n].keys():
                    raise ValueError("%s: arg_type is defined as file, but 'arg_file_path' keyword is missing" % n)
                if not os.path.isfile(os.path.expanduser(self.config[n]['arg_file_path'])):
                    raise ValueError("%s: The arg file %s does not exists" % (n, self.config[n]['arg_file_path']))
            if 'output_type' not in self.config[n].keys():
                raise ValueError("%s: 'output_type' keyword is missing" % n)
            if self.config[n]['output_type'] in ['file' ,'stdout+file'] :
                if 'output_filename' not in self.config[n].keys():
                    raise ValueError("%s: 'output_type' is defined as file, but 'output_filename' keyword is missing" % n)
            if 'local_output_path' not in self.config[n].keys():
                raise ValueError("%s: 'local_output_path' keyword is missing" % n)


    def sync_pids_with_config(self):
        for item in self.all_pids:
            self.config[item[0]]['pid'] = item[1]

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



def run_method_in_parallel(args):
    return args[0].run_remote_job(args[1],args[2],args[3],args[4])

def collect_results_in_parallel(args):
    return args[0].collect_result(args[1],args[2],args[3],args[4])


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
                download_now = arguments.get("--download-now")
                # if len(params_list) != proc_num:
                #     raise ValueError("There should be one parameter for each remote node so that the runs are not identical and redundant.")
                if arguments.get("in:params") and arguments.get("out:stdout"):
                    input_type = "params"
                    output_type = "stdout"
                elif arguments.get("in:params") and arguments.get("out:file"):
                    input_type = "params"
                    output_type = "file"
                    outfile_name = arguments.get("<outfile-name>")
                elif arguments.get("in:params") and arguments.get("out:stdout"):
                    input_type = "params+file"
                    infile_path = arguments.get("<argfile-path>")
                    output_type = "stdout"
                    outfile_name = ''
                elif arguments.get("in:params") and arguments.get("out:stdout"):
                    input_type = "params+file"
                    infile_path = arguments.get("<argfile-path>")
                    output_type = "file"
                    outfile_name = arguments.get("<outfile-name>")
                vcluster_manager.create(config_name,proc_num,download_proc_num,download_now,save_to,input_type,output_type)

        if arguments.get("destroy"):
            if arguments.get("virtual-cluster"):
                vcluster_manager.destroy("virtual-cluster",arguments.get("<virtualcluster-name>"))
            elif arguments.get("runtime-config"):
                vcluster_manager.destroy("runtime-config",arguments.get("<config-name>"))

        if arguments.get("list"):
            if arguments.get("virtual-clusters"):
                max_depth = 1 if arguments.get("<depth>") is None else int(arguments.get("<depth>"))
                vcluster_manager.list("virtual-clusters",max_depth)
            elif arguments.get("runtime-configs"):
                max_depth = 1 if arguments.get("<depth>") is None else int(arguments.get("<depth>"))
                vcluster_manager.list("runtime-configs",max_depth)

        if arguments.get("set-param"):
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
        if arguments.get("run-script"):
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
            params_list = [] if arguments.get("--params") is None else arguments.get("--params").split(',')
            overwrite = False if type(arguments.get("--overwrite")) is None else arguments.get("--overwrite")
            argfile_path = '' if arguments.get("--argfile-path") is None else arguments.get("<argfile-path>")
            outfile_name = '' if arguments.get("--outfile-name") is None else arguments.get("<outfile-name>")
            vcluster_manager.run(job_name,cluster_name,config_name,script_path,argfile_path,outfile_name,remote_path,local_path,params_list,suffix,overwrite)



# if __name__ == '__main__':
#     """
#
#   VirtualCluster.py ssh create [--computers=<computersList>] [--debug]
#     Usage:
#   VirtualCluster.py ssh create --count <vm_number> [--debug]
#   VirtualCluster.py ssh start [--vms=<vmList>] [--debug]
#   VirtualCluster.py ssh stop [--vms=<vmList>] [--debug]
#   VirtualCluster.py ssh destroy [--vms=<vmList>] [--debug]
#   VirtualCluster.py ssh status [--vms=<vmList>]
#   VirtualCluster.py ssh list
#   VirtualCluster.py ssh ssh NAME
#   VirtualCluster.py ssh run-command COMMAND [--vms=<vmList>] [--debug]
#   VirtualCluster.py ssh run-script SCRIPT [--vms=<vmList>] [--debug]
#
#
#     """
#
#     parser.add_argument('--download', metavar='metapath', type=str, nargs=1,
#                         help='Retrieve the result from a previously submitted job using its metadata file.')
#
#
#     if metadatapath is None:
#         all_pids = Manager().list()
#         parallel_jobs = ssh(config_path,output_suffix)
#         all_jobs = [(parallel_jobs,n_idx,n, all_pids) for n_idx,n in enumerate(parallel_jobs.config)]
#         pool = Pool(processes=process_num_submit)
#         pool.map(run_method_in_parallel,all_jobs)
#         parallel_jobs.all_pids = all_pids
#
#         if not nometa:
#             if not os.path.exists('./metadata'):
#                 os.makedirs('./metadata')
#             metadata = parallel_jobs.build_metadata()
#             with open (os.path.join('./metadata','md' + suffix + '.pkl'), "wb") as ff:
#                 pickle.dump(metadata , ff, protocol=pickle.HIGHEST_PROTOCOL)
#             print ("metadata saved.")
#         if nodownload == False:
#             parallel_jobs.sync_pids_with_config()
#             pool = Pool(processes=process_num_collect)
#             print("collecting results")
#             while len(all_pids)> 0 :
#                 time.sleep(3)
#                 all_running_jobs = [(parallel_jobs, n_idx, n, all_pids) for n_idx, n in enumerate(parallel_jobs.config) if (n,parallel_jobs.config[n]['pid']) in all_pids]
#                 pool.map(collect_results_in_parallel, all_running_jobs)
#                 print ("waiting for other results if any...")
#
#             print("All of the remote results collected.")
#     else:
#         if not os.path.isfile(metadatapath):
#             raise FileExistsError("The metadata file %s does not exist."%metadatapath)
#         parallel_jobs = ssh('','',metarun=True)
#         with  open(metadatapath, "rb")  as ff:
#             metadata = pickle.load(ff)
#         parallel_jobs.load_metadata(metadata)
#         all_pids = Manager().list()
#         all_pids.extend(parallel_jobs.all_pids)
#         parallel_jobs.all_pids = all_pids
#         pool = Pool(processes=process_num_collect)
#         print("collecting results")
#         while len(all_pids)> 0 :
#             time.sleep(3)
#             all_running_jobs = [(parallel_jobs, n_idx, n, all_pids) for n_idx, n in enumerate(parallel_jobs.config) if (n,parallel_jobs.config[n]['pid']) in all_pids]
#             pool.map(collect_results_in_parallel, all_running_jobs)
#             print ("waiting for other results if any...")
#         print("All of the remote results collected.")


def main():
    """
    Main function for the SSH. Processes the input arguments.


    """
    arguments = docopt(__doc__, version='Cloudmesh VirtualCluster 0.1')
    process_arguments(arguments)


if __name__ == "__main__":
    main()
