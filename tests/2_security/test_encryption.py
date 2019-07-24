###############################################################
# pytest -v --capture=no tests/1_security/test_encryption.py
# pytest -v  tests/1_security/test_encryption.py
# pytest -v --capture=no  tests/1_security/test_encryption.py:Test_name.<METHIDNAME>
###############################################################
""" run with

pytest -v --capture=no tests/test_encryption.py

"""

import datetime
import os
import shutil
import time

import pytest
from cloudmesh.common.ConfigDict import ConfigDict
from cloudmesh.common.util import path_expand
from cloudmesh.management.configuration.config import Config
from cloudmesh.management.configuration.security.encryption import EncryptFile


# from cloudmesh.management.configuration.security.config import Config


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyPep8Naming,PyBroadException,PyBroadException

@pytest.mark.incremental
class Test_configdict:

    def setup_class(self):

        self.mkdirer()
        self.copy_file()
        self.e = EncryptFile('~/.cloudmesh/tmp/cloudmesh4.yaml',
                             '~/.cloudmesh/tmp/cloudmesh4.yaml.enc', '')

    def mkdirer(self):
        #
        # Shell.mkdir('~/.cloudmesh/tmp') does the same
        #
        path = path_expand('~/.cloudmesh/tmp')
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)

    def copy_file(self):

        source = path_expand('~/.cloudmesh/cloudmesh4.yaml')
        target = path_expand('~/.cloudmesh/tmp')
        shutil.copy(source, target)

    def test_getRandonPassword(self):
        self.e.getRandomPassword()
        # use this for all
        exists = os.path.isfile(path_expand('~/.cloudmesh/key.bin'))
        assert exists
        if exists:
            f = open(path_expand('~/.cloudmesh/key.bin'), 'r')
            password = f.readlines()[0]
            f.close()
        else:
            password = None
        assert len(password) > 20

    def test_encrypt(self):
        self.e.encrypt()
        exists = os.path.isfile(
            path_expand('~/.cloudmesh/tmp/cloudmesh4.yaml.enc'))
        assert exists
        enc_size = os.path.getsize(
            path_expand('~/.cloudmesh/tmp/cloudmesh4.yaml.enc'))
        enc_size = enc_size * 10000 / float(1024 * 1024)
        print(enc_size)
        orginal_size = os.path.getsize(
            path_expand('~/.cloudmesh/tmp/cloudmesh4.yaml'))
        orginal_size = orginal_size * 10000 / float(1024 * 1024)
        print(orginal_size)
        assert abs(enc_size - orginal_size) < 10

    def test_encryptPassword(self):
        self.e.encryptPassword()
        exists = os.path.isfile(path_expand('~/.cloudmesh/key.bin.enc'))
        assert exists
        times = os.path.getmtime(path_expand('~/.cloudmesh/key.bin.enc'))
        timestamp = time.localtime(times)
        fileCreatTime = time.strftime('%Y-%m-%d %H:%M:%S', timestamp)
        print(fileCreatTime)
        currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(currenttime)

        startTime = datetime.datetime.strptime(fileCreatTime,
                                               "%Y-%m-%d %H:%M:%S")
        endTime = datetime.datetime.strptime(currenttime, "%Y-%m-%d %H:%M:%S")
        assert (endTime - startTime).seconds < 4

    def test_decryptRandomKey(self):
        self.e.decryptRandomKey()
        exists = os.path.isfile(path_expand('~/.cloudmesh/key.bin.enc.plain'))
        assert exists
        times = os.path.getmtime(path_expand('~/.cloudmesh/key.bin.enc.plain'))
        timestamp = time.localtime(times)
        fileCreatTime = time.strftime('%Y-%m-%d %H:%M:%S', timestamp)
        print(fileCreatTime)
        currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(currenttime)
        startTime = datetime.datetime.strptime(fileCreatTime,
                                               "%Y-%m-%d %H:%M:%S")
        endTime = datetime.datetime.strptime(currenttime, "%Y-%m-%d %H:%M:%S")
        assert (endTime - startTime).seconds < 4

    def test_decrypt(self):
        self.e.decrypt()
        exists = os.path.isfile(
            path_expand('~/.cloudmesh/tmp/cloudmesh4.yaml.enc.plain'))
        assert exists
        dec_size = os.path.getsize(
            path_expand('~/.cloudmesh/tmp/cloudmesh4.yaml.enc.plain'))
        dec_size = dec_size * 10000 / float(1024 * 1024)
        print(dec_size)
        orginal_size = os.path.getsize(
            path_expand('~/.cloudmesh/tmp/cloudmesh4.yaml'))
        orginal_size = orginal_size * 10000 / float(1024 * 1024)
        print(orginal_size)
        assert abs(dec_size - orginal_size) < 2

    def test_ssh_keygen(self):
        self.e.ssh_keygen()
        for file in os.listdir(path_expand("~/.ssh")):
            file_path = os.path.join(path_expand("~/.ssh"), file)
            if not os.path.isdir(file_path):
                if os.path.splitext(file)[1] == '.pub':
                    flag = True
                    assert flag
                    return

    def test_pem_create(self):
        self.e.pem_create()
        for file in os.listdir(path_expand("~/.ssh")):
            file_path = os.path.join(path_expand("~/.ssh"), file)
            if not os.path.isdir(file_path):
                if os.path.splitext(file)[1] == '.pub':
                    flag = True
                    assert flag
                    return

    def test_pem_verify(self):
        self.e.pem_verify()
        assert True

    def test_set(self):
        filename = path_expand("~/.cloudmesh/tmp/cloudmesh4.yaml")
        key = "cloudmesh.profile.firstname"
        value = "Gregor"
        self.e.set(filename, key, value)
        times = os.path.getmtime(
            path_expand("~/.cloudmesh/tmp/cloudmesh4.yaml"))
        timestamp = time.localtime(times)
        fileUpdateTime = time.strftime('%Y-%m-%d %H:%M:%S', timestamp)
        print(fileUpdateTime)
        currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(currenttime)
        startTime = datetime.datetime.strptime(fileUpdateTime,
                                               "%Y-%m-%d %H:%M:%S")
        endTime = datetime.datetime.strptime(currenttime, "%Y-%m-%d %H:%M:%S")
        assert (endTime - startTime).seconds < 4

    def test__config(self):

        # test original yaml file

        configDict = ConfigDict(path_expand("~/.cloudmesh/cloudmesh4.yaml"))
        assert configDict.__getitem__("meta.version")

        # test tmp_yaml file
        configDict = ConfigDict(path_expand("~/.cloudmesh/tmp/cloudmesh4.yaml"))
        assert configDict.__getitem__("meta.version")

        # test enc_yaml file

        with pytest.raises(UnicodeDecodeError) as e:
            con = Config(path_expand("~/.cloudmesh/tmp/cloudmesh4.yaml.enc"))
            assert con

        # test dec_yaml file
        config = Config(config_path="~/.cloudmesh/cloudmesh4.yaml.enc")
        assert configDict.__getitem__("meta.version")

    def test_edit(self):
        self.e.edit()
        assert True

    def delete_folder(self):
        self.e.delete_folder()
