#!/usr/bin/env python
from __future__ import print_function

"""Vagrant Manager.

Usage:
  vagrant.py vagrant create --count <vm_number> [--debug]
  vagrant.py vagrant start [--vms=<vmList>] [--debug]
  vagrant.py vagrant stop [--vms=<vmList>] [--debug]
  vagrant.py vagrant destroy [--vms=<vmList>] [--debug]
  vagrant.py vagrant status [--vms=<vmList>]
  vagrant.py vagrant list
  vagrant.py vagrant ssh NAME
  vagrant.py vagrant run COMMAND  [--vms=<vmList>]
  vagrant.py vagrant script run SCRIPT [--vms=<vmList>]


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
import fileinput
import re
import subprocess
import os
from docopt import docopt
from colorama import init
from termcolor import colored
import hostlist
import multiprocessing.dummy as mt
import queue


# TODO: workspace should be in ~/.cloudmesh/vagrant
# TODO: if the workspace is not ther it needs to be created
# TODO: use captal letters as easier to document in other tools
# TODO: implement ssh
# TODO: implement the run that executes the command on the specified hosts


class Vagrant(object):
    """
    Vagrant Manager.
    Provides the capabilities to manage a Vagrant Cluster of nodes via the script.
    """

    def __init__(self, debug=False):
        """
        Initializes the workspace for Vagrant.

        :param debug: enables debug information to be printed.
        """
        self.workspace = "./vagrant_workspace"
        self.path = os.path.join(self.workspace, "Vagrantfile")
        self.debug = debug

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

    def run(self, name, command):
        """
        TODO: doc

        :param name:
        """
        res = self.execute('vagrant ssh {} -c {}'.format(name, command), result=True)
        return name, res

    def execute(self, command, result=False):
        """
        TODO: doc

        :param command:
        :return:
        """
        if self.debug:
            print(command.strip())
        else:
            if not result:
                subprocess.run(command.strip(),
                               cwd=self.workspace,
                               check=True,
                               shell=True)
            else:
                try:
                    res = subprocess.check_output(command.strip(),
                                                  cwd=self.workspace,
                                                  shell=True,
                                                  stderr=subprocess.STDOUT)
                    return res
                except Exception as e:
                    return e

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

    if arguments.get("vagrant"):
        provider = Vagrant(debug=debug)
        if arguments.get("create") & arguments.get("--count"):
            provider.generate_vagrantfile(arguments.get("<vm_number>"))

        elif arguments.get("list"):
            provider.list()

        else:
            hosts = False
            action = None

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
            elif arguments.get("run") and arguments.get("COMMAND"):
                action = provider.run
                args = [arguments.get("COMMAND")]
            elif arguments.get("run-script") & arguments.get("SCRIPT"):
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

                elif action_type in ['run', 'run-script']:
                    # make sure there are sth in hosts, if nothing in the host
                    # just grab all hosts in the current vagrant environment
                    if not hosts:
                        hosts = provider._get_host_names()
                        if not hosts:
                            raise EnvironmentError('There is no host exists in the current vagrant project')

                    # initalize threading pool
                    pool = mt.Pool(len(hosts))
                    run_result = queue.Queue()

                    # submit job to the threading pool and (immediately) start execution
                    for node_name in hosts:
                        cur_args = ([node_name] + args)
                        run_result.put(pool.apply_async(action, args=cur_args))
                    pool.close()
                    pool.join()

                    # retrieve the result           
                    while run_result.qsize() > 0:
                        job_res = run_result.get()
                        node_name, res = job_res.get()
                        job_status = 'Success' if not isinstance(res, Exception) else 'Failed'
                        output = res.decode('utf8') if not isinstance(res, Exception) else res.stdout.decode('utf8')

                        ## print report                        
                        template = 'node_name: {}\njob_status: {}\noutput:\n\n{}'
                        print(template.format(node_name, job_status, output))


def main():
    """
    Main function for the Vagrant Manager. Processes the input arguments.
    """
    arguments = docopt(__doc__, version='Cloudmesh Vagrant Manager 0.3')
    process_arguments(arguments)


if __name__ == "__main__":
    main()
