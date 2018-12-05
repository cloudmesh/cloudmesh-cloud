#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 15:49:21 2018

@author: yuluo
"""
import multiprocessing as mp
import subprocess
from os import path

from config import Config


class Run(object):

    def __init__(self, debug=False):
        """
        initializes the run class for awscm

        :param debug: enables debug information to be printed
        """

        self.debug = debug
        self.default_path_aws = '/home/ubuntu/'

    def get_instance(self, instance):
        """
        get the content of the labeled or named instance

        :param instance: the key-value pair of the instance information
        :return instance: the detailed value of the instance
        """

        title = list(instance.keys())[0]
        instance = instance.get(title)

        return instance

    def read_script(self, script):
        """
        read the script file

        :param script: the script that would be run in instance
        :return content: the content of the script
        """

        try:
            content = open(script, "r").read()
            return content
        except:
            return None

    def select_instance(self, scripts):
        """
        select numbers of instances randomly to run the list of scripts

        :param scripts: the list of scripts
        :return task: the list of instance that we can access
        """

        config = Config(debug=False)
        config.config()
        aws = config.get_cloud().get('aws')
        count_scripts = len(scripts)
        count_instance = len(aws)
        task = []

        max_instance = int(count_scripts / count_instance) + 1
        # TODO: BUG: i is over two loops
        for i in range(max_instance):
            for i in aws.keys():
                task.append({i: aws[i]})

        return task

    def run_instance_local(self, instance, scripts):
        # runable for aws
        """
        run the scripts from local to one instance

        :param instance: the instance that we want to access
        :param scripts: the list of running scripts
        :return output: the reuslt of running scripts
        """

        instance = self.get_instance(instance)

        output = []

        if instance.get('address'):
            username = instance.get('address') + "@" + instance.get('credentials').get('username')
            key = instance.get('credentials').get('publickey')
            for i in (str(scripts)).split(','):
                content = ""
                if path.exists(i):
                    content = self.read_script(i)
                else:
                    content = i
                try:
                    temp = subprocess.check_output(['ssh', '-i', key, username, content]).decode("utf-8")
                    output.append('Running script: ' + i + ' in Instance(name) ' + instance.get('name') + ':\n' + temp)
                except:
                    output.append('Cannot run the script ' + i + ' in instance ' + instance.get('name') + ' \n')
        else:
            username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
            key = instance.get('credentials').get('EC2_SECRET_KEY')
            for i in (str(scripts)).split(','):
                content = ""
                if path.exists(i):
                    content = self.read_script(i)
                else:
                    content = i

                try:
                    temp = subprocess.check_output(['ssh', '-i', key, username, content]).decode("utf-8")
                    output.append('Running script: ' + i + ' in Instance(name) ' + instance.get('name') + ':\n' + temp)
                except:
                    output.append('Cannot run the script ' + i + ' in instance(name) ' + instance.get('name') + ' \n')
        return output

    def run_instance_remote(self, instance, scripts):
        # runable for aws
        """
        run the scripts remotely in one instance

        :param instance: the instance that we want to access
        :param scripts: the list of running scripts
        :return output: the reuslt of running scripts
        """

        instance = self.get_instance(instance)
        output = []

        if instance.get('address'):
            username = instance.get('address') + "@" + instance.get('credentials').get('username')
            key = instance.get('credentials').get('publickey')
            for i in (str(scripts)).split(','):
                try:
                    temp = subprocess.check_output(['ssh', '-i', key, username, self.default_path_aws + i]).decode(
                        "utf-8")
                    output.append('Running script: ' + self.default_path_aws + i + ' in Instance(name) ' + instance.get(
                        'name') + ':\n' + temp)
                except:
                    output.append('Cannot run the script ' + i + ' in instance ' + instance.get('name') + ' \n')
        else:
            username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
            key = instance.get('credentials').get('EC2_SECRET_KEY')
            for i in (str(scripts)).split(','):
                try:
                    temp = subprocess.check_output(['ssh', '-i', key, username, self.default_path_aws + i]).decode(
                        "utf-8")
                    output.append('Running script: ' + self.default_path_aws + i + ' in Instance(name) ' + instance.get(
                        'name') + ':\n' + temp)
                except:
                    output.append('Cannot run the script ' + i + ' in instance(name) ' + instance.get('name') + ' \n')
        return output

    def run_local_or_remote(self, scripts, local):
        # runable for aws
        """
        run the scripts from local to paraller instances

        :param local: select run_instance_remote or run_instance_local
        :param scripts: the list of running scripts
        :return output: the reuslt of running scripts
        """

        scripts = scripts.split(',')
        required_instance = self.select_instance(scripts)
        result = []
        queue = mp.Queue()

        def run(instance, script):
            if local:
                r = self.run_instance_local(instance, script)
                queue.put(r)
            else:
                r = self.run_instance_remote(instance, script)
                queue.put(r)

        try:
            process = [mp.Process(target=run, args=(required_instance[i], scripts[i])) for i in range(len(scripts))]

            for i in process:
                i.start()
            for i in process:
                i.join()

            # result = [queue.get() for i in process]
            for i in process:
                result.extend(queue.get())

            return result
        except:
            return ['Parall processing is error, please debug the code']
