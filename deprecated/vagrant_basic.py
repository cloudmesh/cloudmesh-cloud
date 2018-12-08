#!/usr/bin/env python

import logging
import multiprocessing.dummy as mt
import os
import queue
import re
import subprocess
import time

from cm4.configuration.config import Config

#
# TODO: BUG: this is managed laregly with the vm command and not vbox, so what we need to do is make sure that if
#  this stays, we need to have similar fumctionality in vm
#

"""
Implementation notes

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

* added "cm-vbox run" command with multi-threading.

  Design:

    1.   Execute command in the hosts' shell.
    2.   Retrieve the result from hosts' stdout/stderr.
    2.1. Execution result will be retrieved and print to the stdout
    3.   If name of the hosts are not specified using --vms, then the command will 
         execute on all host that registered to the current vbox project.
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


# TODO: workspace should be in ~/.cloudmesh/vbox
# TODO: if the workspace is not ther it needs to be created
# TODO: use captal letters as easier to document in other tools


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
        # prepare path and directory
        self.workspace = os.path.expanduser(os.path.normpath(Config().data['cloudmesh']['cloud']['vbox']['default']['vagrant_path']))
        if not os.path.isdir(self.workspace):
            self._nested_mkdir(self.workspace)
            
        self.path = os.path.join(self.workspace, "Vagrantfile")
        ## if there is no Vagrantfile in the default Vagrantfile path, create one!
        if not os.path.isfile(self.path):
            self.create(count=2)        
        
        self.experiment_path = os.path.join(self.workspace, 'experiment')      
        if not os.path.isdir(self.experiment_path):
            os.mkdir(self.experiment_path)       

        self.ssh_config = {}
        self.debug = debug

    @staticmethod
    def _update_by_key(target, source, keys=None, key_dict=None):
        keys = keys or []
        key_dict = key_dict or {}

        for x in keys:
            if source.get(x):  # key exists and not none
                target.update({re.sub("^[-]+", '', x): source[x]})
        for k, v in key_dict.items():
            if source.get(k):
                target.update({v: source[k]})
        return target

    @staticmethod
    def _impute_drive_sep(splited_path):
        if ':' in splited_path[0]:
            splited_path.insert(0, os.sep)
            splited_path.insert(2, os.sep)
        return splited_path

    @staticmethod
    def _nested_mkdir(path):
        parsed_path = re.split("[\\\\/]", path)
        parsed_path = [x for x in parsed_path if x]
        parsed_path = Vagrant._impute_drive_sep(parsed_path)

        for i in range(len(parsed_path) - 1):
            d = os.path.join(*parsed_path[0:i + 1])
            if not os.path.isdir(d):
                os.mkdir(d)

    def _get_host_names(self):
        """
        get all of the host names that exist in current vbox environment
        """

        #
        # TODO: BUG: should this not also be in the db and if not we load into the db,
        #  but tahan we use the db
        #

        res = self.execute('vbox status', result=True)
        if isinstance(res, Exception):
            print(res)
            return []

        res = res.decode('utf8')
        res = re.split('[\r\n]{1,2}', res)
        host_lines = res[res.index('', 1) + 1:res.index('', 2)]
        host_names = [re.split('\s+', x)[0] for x in host_lines]
        return host_names

    def _scp(self, name, direction, source, dest, recursive):
        """
        upload file to / fetch file from the remote node using scp functionality available on local machine

        :param name: name of the node.
        :param direction: download or upload
        :param source: source file path 
        :param dest: destination file path 
        :return: None
        """
        #
        # TODO: BUG: the scp should work on all named vms, regardless if vbox or not
        #
        # get vbox setting
        if name not in self.ssh_config:
            res = self.execute('vbox ssh-config {}'.format(name), result=True)
            res = res.decode('utf8')
            configs = [x.strip().split() for x in re.split('[\r\n]+', res) if x]
            configs = dict(zip([x[0] for x in configs], [x[1] for x in configs]))
            user = configs['User']
            key_file = os.path.normpath(configs['IdentityFile'])
            ip = configs['HostName']
            port = configs['Port']

            # save to ssh_config
            self.ssh_config[name] = {'user': user, 'ip': ip, 'port': port, 'key_file': key_file}
        else:
            user, ip, port, key_file = [self.ssh_config[name][x] for x in ['user', 'ip', 'port', 'key_file']]

        # submit 
        kwargs = {'recursive': '-r' if recursive else '',
                  'port': port,
                  'key_file': key_file,
                  'source': source,
                  'user': user,
                  'ip': ip,
                  'dest': dest}

        if direction == 'upload':
            logging.debug('upload {} to node {} with path {}...'.format(source, name, dest))
            template = 'scp {recursive} -P {port} -q -o LogLevel=QUIET -o StrictHostKeyChecking=no -i {key_file} {source} {user}@{ip}:{dest}'
            subprocess.call(template.format(**kwargs))
        elif direction == 'download':
            logging.debug('download {} form the node {} with path {}...'.format(source, name, dest))
            template = 'scp {recursive} -P {port} -q -o LogLevel=QUIET -o StrictHostKeyChecking=no -i {key_file} {user}@{ip}:{source} {dest}'
            subprocess.call(template.format(**kwargs))

    @staticmethod
    def _parse_run_result(res, template=None, report_kwargs=None):
        """
        parse running result, and (optionally) generating running report

        :param res: job result object
        :param template: template of running report
        :param report_kwargs: content dictionary of running result
        :return: str or dictionary:
        """
        #
        # TODO: BUG: THis shoudl work on all vms regardless of vbox or not
        #
        # parse run_report
        job_status = 'Finished' if not isinstance(res, Exception) else 'Failed'

        if job_status == 'Finished':
            str_output = res.decode('utf8') if not isinstance(res, str) else res
            command_output = re.search('^\x04(.+?)\nreturn_code', str_output, re.MULTILINE | re.DOTALL)
            command_output = command_output.group(1).strip() if command_output else ""
            return_code = int(re.search('return_code: (\d+)', str_output).group(1))
            job_status = job_status if return_code != 0 else 'Success'
        else:
            command_output = res.stdout.decode('utf8')
            return_code = 'N.A.'

        parse_result = {'job_status': job_status, 'return_code': return_code, 'output': command_output}
        if template and report_kwargs:
            report_kwargs.update(parse_result)
            return template.format(**report_kwargs)
        else:
            return parse_result

    @staticmethod
    def run_parallel(hosts, run_action, args, kwargs):
        """
        run job in parallel fashion

        :param hosts: list of node names on which job runs
        :param run_action: running action function object
        :param args: positional arguments of running action function
        :param kwargs: keyword arguments of running action function
        :return: None:
        """
        #
        # TODO: BUG: This shoudl work on all vms regardless of vbox or not
        #
        # initalize threading pool
        pool = mt.Pool(len(hosts))
        run_result = queue.Queue()

        # submit job to the threading pool and put the job result object into the result queue
        for node in hosts:
            currrent_args = ([node] + args)
            job = pool.apply_async(run_action, args=currrent_args, kwds=kwargs)
            run_result.put([node, job])
        pool.close()

        # retrieve the result          
        wait_time = 5
        run_report = []
        try:
            while run_result.qsize() > 0:
                node, job_res = run_result.get()
                if not job_res.ready():
                    run_result.put([node, job_res])
                    logging.info('job assign to node {:<8s} is not finished yet! Wait for finishing.....'.format(node,
                                                                                                                 wait_time))
                    time.sleep(wait_time)
                else:
                    run_report.append(job_res.get())
        except KeyboardInterrupt:
            pass

        # print report
        for x in run_report:
            print(x)

    def run_script(self, name, script_path, data=None, report=True, report_alone=True):
        """
        run shell script on specified node, fetch the console output and data output if existed

        :param data:
        :param name: name of node
        :param script_path: local path of script file which will be executed on the node
        :param report: processing job running report. if False, return result object
        :param report_alone: print job running report. if False, return job running report
        :return: dictionary, subprocess.CalledProcessError
        """

        #
        # TODO: BUG: This should work on all vms and not just vbox
        #

        # building path
        script_name = os.path.basename(script_path)
        exp_folder_name = '{}_{:.0f}'.format(script_name, time.time())
        guest_exp_folder_path = '~/cm_experiment/{}'.format(exp_folder_name)
        guest_script_path = '{}/{}'.format(guest_exp_folder_path, script_name)

        # ensure cm_experiment folder exists, in not, build cm_experiement folder
        cm_folder_query = self.run_command(name, 'ls -d ~/cm_experiment/', False)
        cm_folder_query = cm_folder_query['output']
        if 'No such file or directory' in cm_folder_query:
            self.run_command(name, 'mkdir ~/cm_experiment', False)

        # build guest experiment folder and ship script to it
        self.run_command(name, 'mkdir {}'.format(guest_exp_folder_path), False)
        self.upload(name, source=script_path, dest=guest_script_path, recursive=False)

        # if there is some data must running against, scp data to data folder
        if data:
            if os.path.isdir(data):
                self.upload(name, source=data, dest=guest_exp_folder_path, recursive=True)
                data_folder = [x for x in re.split('[\\\\/]', data) if x][-1]
                self.run_command(name, 'mv {base}/{data_folder} {base}/data'.format(base=guest_exp_folder_path,
                                                                                    data_folder=data_folder), False)
            else:
                data_folder = '{}/data/'.format(guest_exp_folder_path)
                self.run_command(name, 'mkdir {}'.format(data_folder), False)
                self.upload(name, source=data, dest=data_folder)

        # run the script
        script_args = guest_exp_folder_path
        run_res = self.run_command(name, '. {} {} 2>&1 > {}/console_output.txt'.format(guest_script_path, script_args,
                                                                                       guest_exp_folder_path), False)

        # fetch console output
        if isinstance(run_res, subprocess.CalledProcessError):
            # TODO: if return error, how to modify the following process?
            pass
        elif isinstance(run_res, Exception):
            raise run_res
        else:
            console_output = self.run_command(name, 'cat {}/console_output.txt'.format(guest_exp_folder_path), False)
            run_res['output'] = console_output['output'] + '\n' + run_res['output']

        # fetch output files if exists
        output_files_query = self.run_command(name, "ls {}/output/".format(guest_exp_folder_path), report=False)
        have_output_file = output_files_query['return_code'] == 0 and output_files_query[
            'output']  # remote output folder exists and have files in it

        if have_output_file:
            # build local experiment folder
            host_exp_folder_path = os.path.join(self.experiment_path, name, exp_folder_name, 'output')
            self._nested_mkdir(host_exp_folder_path)
            self.download(name, source="{}/output/".format(guest_exp_folder_path), dest=host_exp_folder_path,
                          prefix_dest=False, recursive=True)

        # processing the report
        if not report:
            return run_res

        else:
            host_exp_folder_path = os.path.join(self.experiment_path, name, exp_folder_name, 'output')

            template = '\n'.join(['\n\n========= JOB REPORT =========',
                                  'node_name: {name}',
                                  'job_description: {job_type} "{command}"',
                                  'job_status/node_return_code: {job_status} / {return_code}',
                                  'node_job_folder: {remote_job_folder}',
                                  'local_output_folder:{local_output_folder}',
                                  'console_output:\n{output}\n'])

            report_kwargs = {'name': name,
                             'job_type': 'run_script',
                             'remote_job_folder': guest_exp_folder_path + '/',
                             'local_output_folder': host_exp_folder_path + '/' if have_output_file else 'N.A.',
                             'command': script_path
                             }

            report_kwargs.update(run_res)
            report = template.format(**report_kwargs)

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
        # submit job

        #
        # TODO: BUG: THis shoudl work on all vms and not just vbox
        #
        logging.debug('exceute "{}" on node {}......'.format(command, name))
        res = self.execute(
            'vbox ssh {} -c "echo -e \\"\x04\\";{}; echo \\"return_code: $?\\""'.format(name, command), result=True)

        # processing result
        if not report:
            return self._parse_run_result(res) if not isinstance(res, Exception) else res

        else:
            template = '\n'.join(['\n\n========= JOB REPORT =========',
                                  'node_name: {name}',
                                  'job_description: {job_type} "{command}"',
                                  'console output:\n{output}\n'])
            report_kwargs = {'name': name, 'job_type': 'run_command', 'command': command}
            report = self._parse_run_result(res, template, report_kwargs)

            if report_alone:
                print(report)
            else:
                return report

    def execute(self, command, result=False):
        """
        TODO: doc

        :param result:
        :param command:
        :return:
        """
        if self.debug:
            logging.debug(command.strip())
            logging.debug(self.workspace.strip())

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
        self.execute("vbox ssh " + str(name))

    def create(self, count=2, image='ubuntu/xenial64', output_path=None, template=None):
        """
        TODO: doc

        :return:                        
        """
        # prepare dict
        
        kwargs = {}
        count = int(count)
        array = ["'{}{}'".format(x,y) for x,y in zip(['node'] * count, list(range(1,1+count)))]
        kwargs.update({'array': ','.join(array)})
        kwargs.update({'image': image})

        # prepare template
        if not template:
            template = """
            Vagrant.configure("2") do |config|    
              ([{array}]).each do |name|
                config.vm.define "#{{name}}" do |node|
                  node.vm.box = "{image}"
                end
              end
            end
            """

        # write
        if not output_path:
            output_path = self.path
        with open(output_path, 'w') as out:
            out.write(template.format(**kwargs))

    def start(self, name=None):
        """
        Default: Starts all the VMs specified.
        If @name is provided, only the named VM is started.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vbox up " + str(name))

    def resume(self, name=None):
        """
        Default: resume(start) all the VMs specified.
        If @name is provided, only the named VM is started.

        :param name: [optional], name of the Vagrant VM.
        :return:
        """

        if name is None:
            # start all
            name = ""
        self.execute("vbox up " + str(name))

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
        self.execute("vbox halt " + str(name))

    def suspend(self, name=None):
        """
        TODO: doc

        :param name:
        :return:
        """
        if name is None:
            # start all
            name = ""
        self.execute("vbox suspend " + str(name))

    def destroy(self, name=None, force=False):
        """
        Default: Destroys all the VMs specified.
        If @name is provided, only the named VM is destroyed.

        :param force:
        :param name: [optional], name of the Vagrant VM.
        :return:
        """
        if name is None:
            name = ""
        self.execute("vbox destroy {}{}".format('-f ' if force else '', name))

    def list(self):
        """
        Provides the status information of all Vagrant Virtual machines.
        """        
        self.execute("vbox status")

    def status(self, name):
        """
        provides the status of that particular virtual machine.

        :return:
        """
        self.execute("vbox status " + name)

    def download(self, name, source, dest, prefix_dest=False, recursive=False):
        """
        TODO: doc

        :return:
        """
        if prefix_dest:
            if os.path.isdir(dest):
                dest = os.path.join(dest, name)
                if not os.path.isdir(dest):
                    os.mkdir(dest)
            else:
                path_split = re.split('[\\\\/]', dest)
                if path_split[-1]:
                    path_split.insert(-1, name)
                    path_split = self._impute_drive_sep(path_split)
                    dest = os.path.join(*path_split)

        r = (not os.path.basename(source) or recursive)
        self._scp(name, 'download', source, dest, r)

    def upload(self, name, source, dest, recursive=False):
        """
        TODO: doc

        :return:
        """
        r = (not os.path.basename(source) or recursive)
        self._scp(name, 'upload', source, dest, r)

