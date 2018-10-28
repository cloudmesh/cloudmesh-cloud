#!/usr/bin/env python

"""Vagrant Manager.

Usage:
  vagrant.py vagrant create --count <vm_number> [--debug]
  vagrant.py vagrant start [--vms=<vmList>] [--debug]
  vagrant.py vagrant stop [--vms=<vmList>] [--debug]
  vagrant.py vagrant destroy [--vms=<vmList>] [--debug]
  vagrant.py vagrant status [--vms=<vmList>]
  vagrant.py vagrant list
  vagrant.py vagrant ssh NAME
  vagrant.py vagrant run-command COMMAND [--vms=<vmList>] [--debug]
  vagrant.py vagrant run-script SCRIPT [--vms=<vmList>] [--debug]



  vagrant.py -h

Options:
  -h --help     Show this screen.
  --vm_list=<list_of_vms>  List of VMs separated by commas ex: node-1,node-2

Description:
   put a description here
   
Example:
   put an example here
"""
"""
Inplementation notes


Future Version ideas:

* Discuss how to  run a script on in many vm's
  e.g. mabye we need another new command?
  `scripy run SCRIPT` command, as suggested in the file's doc.
* Question: could the code after elif action_type in ['run','run-script']:
  be moved into a function/class?
* do we need to adopt the logic from cloudmesh/experiment, where we create 
  a directory for each machine.vm and store the output files there. e.g.
  --output=experiment
 
     experiment/vm1/outout files from vm 1 go here 
     experiment/vm2/outout files from vm 2 go here 
     ...
* use capital letters only and not <value>, e.g. VALUE instead of <value> in docots spec

Version 0.3:

* addes "cm-vagrant run" command with multi-threading.

  Design:

    1.   Execute command in the hosts' shell.
    2.   Retrieve the result from hosts' stdout/stderr.
    2.1. Execution result will be retrieved and print to the stdout
    3.   If name of the hosts are not specified using --vms, then the command will 
         execute on all host that registered to the current vagrant project.
    3.1. However, if the hosts are not available through ssh when running 
         (say, the vm is stopped) , the execution will failed.
    4.   For every run command, every specified host will run the command 
         exactly one time, in a parrallelized fashion. The execution on every 
         machine will be handled by a seperated thread.

* additional changes to code and do some minor correction.


Version 0.2:

* added hostlists
* simplified argument processing
* introduced class object for management
* added templates for documentation


Version 0.1:

* basic docopts version with elementary functionality
* no classes

"""

# TODO: workspace should be in ~/.cloudmesh/vagrant
# TODO: if the workspace is not ther it needs to be created
# TODO: use captal letters as easier to document in other tools


import queue
import fileinput
import re
import subprocess
import os
import hostlist
from docopt import docopt
from colorama import init
from termcolor import colored
import multiprocessing.dummy as mt
import time
import logging

class Vagrant(object):
    """
    Vagrant Manager.
    Provides the capabilities to manage a Vagrant Cluster of nodes via the script.
    """

    def __init__(self, debug=False):
        """
        TODO: doc

        :param debug:
        """
        self.workspace = "./vagrant_workspace"
        self.experiment_path="../experiment"
        self.ssh_config={}
        self.path = os.path.join(self.workspace, "Vagrantfile")
        self.debug = debug

    def _nested_mkdir(self, path):
        parsed_path=path.split('/')
        for i in range(len(parsed_path)-1):
            d='/'.join(parsed_path[0:i+1])
            if not os.path.isdir(d):
                os.mkdir(d)
                
    def _get_host_names(self):
        """
        get all of the host names that exist in current vagrant environment
        """
        res = self.execute('vagrant status', result=True)
        if isinstance(res, Exception):
            print(res)
            return []
            
        res = res.decode('utf8')
        res = re.split('[\r\n]{1,2}', res)
        host_lines = res[res.index('', 1) + 1:res.index('', 2)]
        host_names = [re.split('\s+', x)[0] for x in host_lines]
        return host_names

    def _scp(self,name, direction, source, dest):
        """
        upload file to / fetch file from the remote node using scp functionality available on local machine

        :param name: name of the node.
        :param direction: download or upload
        :param source: source file path 
        :param dest: destination file path 
        :return: None
        """         
        # get vagrant setting
        if name not in self.ssh_config:
            res=self.execute('vagrant ssh-config {}'.format(name), result=True)
            res=res.decode('utf8')            
            configs=[x.strip().split() for x in re.split('[\r\n]+',res) if x]
            configs=dict(zip([x[0] for x in configs], [x[1] for x in configs]))
            user=configs['User']
            key_file=os.path.normpath(configs['IdentityFile'])
            
            # get node ip
            res=self.run_command(name, 'hostname -I', False)    
            ip=re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', res['output'])[1]
            
            #save to ssh_config
            self.ssh_config[name]={'user':user, 'ip':ip, 'key_file':key_file}
        else:
            user, ip, key_file=[self.ssh_config[name][x] for x in ['user','ip','key_file']]
            
        # submit 
        kwargs={'key_file':key_file, 'source':source, 'user':user, 'ip':ip, 'dest':dest}
        
        if direction=='upload':
            logging.debug('upload {} to node {}...'.format(source, name))
            subprocess.call('scp -q -o LogLevel=QUIET -i {key_file} {source} {user}@{ip}:{dest}'.format(**kwargs))
        elif direction=='download':
            logging.debug('download {} form the node {}...'.format(source, name))
            subprocess.call('scp -q -o LogLevel=QUIET -i {key_file} {user}@{ip}:{source} {dest}'.format(**kwargs))
                     
    def _parse_run_result(self, res, template=None, report_kwargs=None):
        """
        parse runnin result, and (optionally) generating running report

        :param res: job result object
        :param template: template of running report
        :param report_kwargs: content dictionary of running result
        :return: str or dictionary:
        """         
        #parse run_report
        job_status='Finished' if not isinstance(res, Exception) else 'Failed'
        
        if job_status =='Finished':
            str_output=res.decode('utf8') if not isinstance(res, str) else res
            command_output=re.search('^\x04(.+?)\nreturn_code', str_output, re.MULTILINE|re.DOTALL)
            command_output=command_output.group(1).strip() if command_output else ""
            return_code=int(re.search('return_code: (\d+)', str_output).group(1))
            job_status=job_status if return_code!=0 else 'Success'
        else:                               
            command_output=res.stdout.decode('utf8')
            return_code='N.A.'
        
        ## return 
        parse_result={'job_status':job_status, 'return_code':return_code, 'output':command_output}
        if template and report_kwargs:
            report_kwargs.update(parse_result)
            return template.format(**report_kwargs)
        else:
            return parse_result

    def run_parallel(self, hosts, action, args, kwargs):                                            
        """
        run job in parallel fashion

        :param hosts: list of node names on which job runs
        :param run_action: running action function object
        :param args: positional arguments of running action function
        :param kwargs: keyword arguments of running action function
        :return: None:
        """      
        # initalize threading pool
        pool = mt.Pool(len(hosts))
        run_result = queue.Queue()
        
        # submit job to the threading pool and put the job result object into the result queue
        for node in hosts:
            currrent_args = ([node] + args)
            job=pool.apply_async(action, args=currrent_args, kwds=kwargs)            
            run_result.put([node, job])
        pool.close()
        
        # retrieve the result          
        wait_time=5
        run_report=[]
        while run_result.qsize()>0:
            node, job_res = run_result.get()
            if not job_res.ready():
                run_result.put([node, job_res])
                logging.info('job assign to node {:<8s} is not finished yet! Wait for finishing.....'.format(node, wait_time))
                time.sleep(wait_time)
            else:
                run_report.append(job_res.get())
        
        #print report
        for x in run_report:
            print(x)
                
    def run_script(self, name, script_path, report=True, report_alone=True):
        """
        run shell script on specified node, fetch the console output and data output if existed

        :param name: name of node
        :param script_path: local path of script file which will be executed on the node
        :param report: processing job running report. if False, return result object
        :param report_alone: print job running report. if False, return job running report
        :return: dictionary, subprocess.CalledProcessError
        """
        # building path
        script_name=os.path.basename(script_path)
        exp_folder_name='{}_{:.0f}'.format(script_name,time.time())
        guest_exp_folder_path='~/cm_experiment/{}'.format(exp_folder_name)
        guest_script_path='{}/{}'.format(guest_exp_folder_path,script_name)

        # ensure cm_experiment folder exists, in not, build cm_experiement folder
        cm_folder_query=self.run_command(name, 'ls -d ~/cm_experiment/', False)
        cm_folder_query=cm_folder_query['output']
        if 'No such file or directory' in cm_folder_query:
            self.run_command(name, 'mkdir ~/cm_experiment', False)
                           
        # build geust expreiment folder and ship sciript to it 
        self.run_command(name, 'mkdir {}'.format(guest_exp_folder_path), False)
        self._scp(name, 'upload', source=script_name, dest=guest_script_path)
      
        # run the script
        script_args=guest_exp_folder_path
        run_res=self.run_command(name, '. {} {} 2>&1 > {}/console_output.txt'.format(guest_script_path, script_args, guest_exp_folder_path), False)   
        
        # fetch console output
        if isinstance(run_res, subprocess.CalledProcessError):
            # TODO: if return error, how to modify the following process?
            pass
        elif isinstance(run_res, Exception):
            raise run_res
        else:
            console_output=self.run_command(name, 'cat {}/console_output.txt'.format(guest_exp_folder_path), False)
            run_res['output']=console_output['output']+'\n'+run_res['output']               
        
        # fetch output files if exists
        output_files_query=self.run_command(name, "ls {}/output/".format(guest_exp_folder_path), report=False)
        have_output_file=output_files_query['return_code']==0 and output_files_query['output'] # remote output folder exists and have files in it     
        
        if have_output_file:
            # build local experiment folder
            host_exp_folder_path='{}/{}/{}/output'.format(self.experiment_path, name, exp_folder_name)  
            self._nested_mkdir(host_exp_folder_path)
            
            #fetch output files
            output_files=[ '{}/output/{}'.format(guest_exp_folder_path, x) for x in output_files_query['output'].split('\n')]
            for source in output_files:
                self._scp(name, 'download', source=source, dest=host_exp_folder_path)
 
        # processing the report
        if not report:
            return run_res
        
        else:
            template='\n'.join(['\n\n========= JOB REPORT =========',
                                'node_name: {name}',
                                'job_description: {job_type} "{command}"',
                                'job_status/node_return_code: {job_status} / {return_code}',
                                'node_job_folder: {remote_job_folder}',
                                'local_output_folder:{local_output_folder}',
                                'console_output:\n{output}\n'])            
            
            report_kwargs={'name':name, 
                           'job_type':'run_script',
                           'remote_job_folder':guest_exp_folder_path+'/',
                           'local_output_folder': host_exp_folder_path+'/' if have_output_file else 'N.A.',
                           'command':script_path                          
                           }
            
            report_kwargs.update(run_res)            
            report=template.format(**report_kwargs)
            
            if report_alone:
                print(report)            
            else:
                return report            
            
    def run_command(self, name, command, report=True, report_alone=True):
        """
        run shell command in specified node

        :param name: name of node
        :param command: command executed on the node
        :param report: processing job running report. if False, return result object
        :param report_alone: print job running report. if False, return job running report
        :return: string, subprocess.CalledProcessError
        """
        #submit job
        logging.debug('exceute "{}" on node {}......'.format(command, name))        
        res=self.execute('vagrant ssh {} -c "echo -e \\"\x04\\";{}; echo \\"return_code: $?\\""'.format(name, command), result=True)                                       
        
        # processing result
        if not report:
            return self._parse_run_result(res) if not isinstance(res, Exception) else res
        
        else:
            template='\n'.join(['\n\n========= JOB REPORT =========',
                                'node_name: {name}',
                                'job_description: {job_type} "{command}"',
                                'console output:\n{output}\n'])
            report_kwargs={'name':name, 'job_type':'run_command', 'command':command}
            report=self._parse_run_result(res, template, report_kwargs)
            
            if report_alone:
                print(report)                
            else:
                return report                
											 
							  
    def execute(self, command, result=False):
        """
        TODO: doc

        :param command:
        :return:
        """
        if self.debug:
            logging.debug(command.strip())
	  

        if not result:
            subprocess.run(command.strip(),
                           cwd=self.workspace,
                           check=True,
                           input=b'\n',
                           shell=True)
        else:
            try:
                res = subprocess.check_output(command.strip(),
                                              cwd=self.workspace,
                                              shell=True,
                                              input=b'\n',
                                              stderr=subprocess.STDOUT)
                return res
            except Exception as e:
                return e
				
    def ssh(self, name):
        """
        TODO: doc
		
        :param name:
        :return:
        """				 
        self.execute("vagrant ssh " + str(name))
					
			
    def status(self, name=None):
        """
        Provides the status information of all Vagrant Virtual machines by default.
        If a name is specified, it provides the status of that particular virtual machine.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vagrant status " + str(name))

    def vagrant_action(self, action=None, name=None):
        """
        TODO: doc

        :param name:
        :return:
        """
        if action is None:
            pass  # error
        if name is None:
            # start all
            name = ""
        self.execute("vagrant " + action + " " + str(name))

    def start(self, name=None):
        """
        Default: Starts all the VMs specified.
        If @name is provided, only the named VM is started.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        self.vagrant_action(action="start", name=name)
					   	   

    def stop(self, name=None):
        """
        Default: Stops all the VMs specified.
        If @name is provided, only the named VM is stopped.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vagrant halt " + str(name))

    def destroy(self, name=None):
        """
        Default: Destroys all the VMs specified.
        If @name is provided, only the named VM is destroyed.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            name = ""
        self.execute("vagrant destroy " + str(name))

    def generate_vagrantfile(self, number_of_nodes):
        """
        Generates the Vagrant file to support the @number_of_nodes

        :param number_of_nodes: number of nodes required in the cluster.
        """
        replacement_string = "NUMBER_OF_NODES = " + str(number_of_nodes)
        for line in fileinput.FileInput(os.path.join(self.path), inplace=True):
            line = re.sub("NUMBER_OF_NODES.*(\d+)$", replacement_string, line.rstrip())
            print(line)

    def list(self):
        """
        TODO: doc

        :return:
        """
        with open(self.path, 'r') as f:
            content = f.read()
        print(content)


def process_arguments(arguments):
    """
    Processes all the input arguments and acts accordingly.

    :param arguments: input arguments for the Vagrant script.
			
    """
    debug = arguments["--debug"]
    if debug:
        try:
            columns, rows = os.get_terminal_size(0)
        except OSError:
            columns, rows = os.get_terminal_size(1)

        print(colored(columns * '=', "red"))
        print(colored("Running in Debug Mode", "red"))
        print(colored(columns * '=', "red"))
        print(arguments)
        print(colored(columns * '-', "red"))
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


    if arguments.get("vagrant"):
        provider = Vagrant(debug=debug)
        if arguments.get("create") & arguments.get("--count"):
            provider.generate_vagrantfile(arguments.get("<vm_number>"))

        elif arguments.get("list"):
            provider.list()

        else:
            hosts = False
            action = None
            kwargs = dict()
            args= ()

            if arguments.get("--vms"):
                hosts = arguments.get("--vms")
                hosts = hostlist.expand_hostlist(hosts)

            if arguments.get("start"):
                action = provider.start
            elif arguments.get("stop"):
                action = provider.stop
            elif arguments.get("destroy"):
                action = provider.destroy
            elif arguments.get("status"):
                action = provider.status
            elif arguments.get("ssh"):
                action = provider.ssh
                args=[arguments.get("NAME")]
            elif arguments.get("run-command") and arguments.get("COMMAND"):
                action = provider.run_command
                args = [arguments.get("COMMAND")]
            elif arguments.get("run-script") and arguments.get("SCRIPT"):
                action = provider.run_script
                args = [arguments.get("SCRIPT")]
              

            # do the action
            if action is not None:
                action_type = action.__name__
                if action_type in ['start', 'stop', 'destroy', 'status']:
                    if hosts:
                        for node_name in hosts:
                            action(node_name)
                    else:
                        action()

                elif action_type in ['ssh']:
                    action(*args)
                
                elif action_type in ['run_command','run_script']:                 
                    # make sure there are sth in hosts, if nothing in the host
                    # just grab all hosts in the current vagrant environment
                    if not hosts:
                        hosts = provider._get_host_names()
                        if not hosts:
                            raise EnvironmentError('There is no host exists in the current vagrant project')
			  
                    if len(hosts)>1:
                        kwargs.update({'report_alone':False})				
                        provider.run_parallel(hosts, action, args, kwargs)
                    else:
                        kwargs.update({'report_alone':True})
                        action(hosts[0], *args, **kwargs)                   

def main():
    """
    Main function for the Vagrant Manager. Processes the input arguments.

			
    """
    arguments = docopt(__doc__, version='Cloudmesh Vagrant Manager 0.3')
    process_arguments(arguments)


if __name__ == "__main__":
    main()
