#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 19:15:04 2018

@author: yuluo
"""
import subprocess


class Utility(object):

    def __init__(self, debug=False):
        """
        initializes the utulity class for awscm

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

    def copy_file(self, instance, file, where):
        # runable for aws
        """
        copy the file from local into the instance

        :param instance: the instance that we want to access
        :param file: the file path that we want to copy to the instance
        :param where: the destination of the copied file
        :return: "Success" or "Fail"
        """

        instance = self.get_instance(instance)
        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                subprocess.check_output(["scp", key, file, username + ":" + self.default_path_aws + where])
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                subprocess.check_output(["scp", "-i", key, file, username + ":" + self.default_path_aws + where])
            return "Success to copy the file " + file + " to " + self.default_path_aws + where
        except:
            return "Fail to access the instance"

    def copy_folder(self, instance, folder, where):
        # runable for aws
        """
        copy the folder from local into the instance

        :param instance: the instance that we want to access
        :param folder: the folder path that we want to copy to the instance
        :param where: the destination of the copied file
        :return: "Success" or "Fail"
        """

        instance = self.get_instance(instance)
        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                subprocess.check_output(["scp", key, "-r", folder, username + ":" + self.default_path_aws + where])
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                subprocess.check_output(
                    ["scp", "-i", key, "-r", folder, username + ":" + self.default_path_aws + where])
            return "Success to copy the folder " + folder + " to " + self.default_path_aws + where
        except:
            return "Fail to access the instance"

    def dir_list(self, instance, where):
        """
        list objects from the instance directory

        :param instance: the instance we want to access
        :param where: the directory that we want to view
        :return output: the list of objects
        """

        instance = self.get_instance(instance)
        output = ''

        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                output = subprocess.check_output(["ssh", key, username, 'ls', self.default_path_aws + where]).decode(
                    "utf-8")
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                output = subprocess.check_output(
                    ["ssh", "-i", key, username, 'ls', self.default_path_aws + where]).decode("utf-8")
            return output
        except:
            return "Fail to access the instance"

    def delete_file(self, instance, file, where):
        """
        delete the file from the instance

        :param instance: the instance that we want to access
        :param file: the file name that we want to delete
        :param where: the destination of the deleted file
        :return: "Success" or "Fail"
        """

        instance = self.get_instance(instance)
        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                subprocess.check_output(["ssh", key, username, 'rm', self.default_path_aws + where + file])
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                subprocess.check_output(["ssh", "-i", key, username, 'rm', self.default_path_aws + where + file])
            return "Success to delete the file " + file + " from " + self.default_path_aws + where
        except:
            return "Fail to access the instance"

    def delete_folder(self, instance, folder, where):
        """
        delete the folder from the instance

        :param instance: the instance that we want to access
        :param folder: the folder name that we want to delete
        :param where: the destination of the deleted folder
        :return: "Success" or "Fail"
        """

        instance = self.get_instance(instance)
        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                subprocess.check_output(["ssh", key, username, 'rm', '-r', self.default_path_aws + where + folder])
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                subprocess.check_output(
                    ["ssh", "-i", key, username, 'rm', '-r', self.default_path_aws + where + folder])
            return "Success to delete the folder " + folder + " from " + self.default_path_aws + where
        except:
            return "Fail to access the instance"

    def create_folder(self, instance, folder, where):
        """
        create a folder in the instance

        :param instance: the instance that we want to access
        :param folder: the name of created folder
        :param where: the destination location in the remote instance
        :return: "Success" or "Fail"
        """

        instance = self.get_instance(instance)
        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                subprocess.check_output(["ssh", key, username, 'mkdir', self.default_path_aws + where + folder])
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                subprocess.check_output(["ssh", "-i", key, username, 'mkdir', self.default_path_aws + where + folder])
            return "Success to create the folder " + folder + " in " + self.default_path_aws + where
        except:
            return "Faile to access the instance"

    def read_file(self, instance, file, where):
        """
        read file from the instance

        :param instance: the instance that we want to access
        :param file: the file name that we want to read
        :param where: the location of the file in the instance
        :return output: the content of file
        """

        instance = self.get_instance(instance)
        output = ""
        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                output = subprocess.check_output(
                    ["ssh", key, username, 'cat', self.default_path_aws + where + file]).decode("utf-8")
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                output = subprocess.check_output(
                    ["ssh", "-i", key, username, 'cat', self.default_path_aws + where + file]).decode("utf-8")
            return output
        except:
            return "Faile to access the instance"

    def download_file(self, instance, file, where, local):
        """
        download file from instance to local

        :param instance: the instance that we want to access
        :param file: the file name that we want to download
        :param where: the directory path of the file in the instance
        :param local: the local destination that we want to save the file
        :return: "Success" or "Fail"
        """

        instance = self.get_instance(instance)

        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                subprocess.check_output(["scp", key, username + ":" + self.default_path_aws + where + file, local])
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                subprocess.check_output(
                    ["scp", "-i", key, username + ':' + self.default_path_aws + where + file, local])
            return "Success to download file " + self.default_path_aws + where + file + " to " + local
        except:
            return "Faile to access the instance"

    def download_folder(self, instance, folder, where, local):
        """
        download folder from instance to local

        :param instance: the instance that we want to access
        :param folder: the folder name that we want to download
        :param where: the directory path of the folder in the instance
        :param local: the local destination that we want to save the folder
        :return: "Success" or "Fail"
        """

        instance = self.get_instance(instance)

        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                subprocess.check_output(
                    ["scp", key, '-r', username + ":" + self.default_path_aws + where + folder, local])
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                subprocess.check_output(
                    ["scp", "-i", key, '-r', username + ':' + self.default_path_aws + where + folder, local])
            return "Success to download folder " + self.default_path_aws + where + folder + " to " + local
        except:
            return "Faile to access the instance"

    def check_process(self, instance, process):
        """
        check where the process is running or not

        :param instance: the instance that we want to access
        :param process: the process name
        :return output: the information of the running process
        """

        instance = self.get_instance(instance)
        output = ""
        try:
            if instance.get('address'):
                username = instance.get('address') + "@" + instance.get('credentials').get('username')
                key = instance.get('credentials').get('publickey')
                output = subprocess.check_output(["ssh", key, username, 'ps', 'aux', '|', 'grep', process]).decode(
                    "utf-8")
            else:
                username = 'ubuntu@' + instance.get('credentials').get('EC2_ACCESS_ID')
                key = instance.get('credentials').get('EC2_SECRET_KEY')
                # output = os.popen("ls"+ " | " + "ssh"+ " -i "+ key +" "+ username).read()
                output = subprocess.check_output(
                    ["ssh", '-i', key, username, 'ps', 'aux', '|', 'grep', process]).decode("utf-8")
            return output
        except:
            return "Faile to access the instance"
