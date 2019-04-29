import os
from cloudmesh.common.util import path_expand
import os
from cloudmesh.common.util import path_expand
from cloudmesh.common.dotdict import dotdict
from cloudmesh.DEBUG import VERBOSE
import platform
from getpass import getpass
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.ConfigDict import ConfigDict
import shutil

class EncryptFile(object):
    def __init__(self, file_in, file_out, certificate,debug=False,):
        plain_file = file_out + '.plain'
        self.data = {
            'file_in': file_in,
            'file_out': file_out,
            'file_out_plain': plain_file,
            'certificate': certificate,
            'pem': path_expand('~/.ssh/id_rsa.pub.pem'),
            'key': path_expand(' ~/.ssh/id_rsa'),
            'password': path_expand('~/.cloudmesh/key.bin'),
            'password_enc': path_expand('~/.cloudmesh/key.bin.enc'),
            'password_enc_plain': path_expand('~/.cloudmesh/key.bin.enc.plain')
        }
        self.debug = debug

    def _execute(self, command):
        if self.debug:
            print(command)
        os.system(command)

    '''
    def encrypt(self):
        # encrypt the file into secret.txt
        print(self.data)
        command = path_expand(
            "openssl rsautl -encrypt -pubin -inkey {pem} -in {file} -out {secret}".format(**self.data))
        self._execute(command)

    def decrypt(self, filename=None,decrypted_file=None):
        if filename is not None:
            self.data['secret'] = filename
            self.data['file'] = decrypted_file

        command = path_expand("openssl rsautl -decrypt -inkey {key} -in {secret} -out {file}".format(**self.data))
        self._execute(command)
    '''


    # extract public key from a certificate
    def getPublicKey(self):
        command = path_expand(
            "openssl rsa -in {certificate} -out {pem} -outform PEM -pubout".format(**self.data))
        self._execute(command)


    # Generate the random password file
    def getRandonPassword(self):
        command = path_expand(
            "openssl rand -hex 64 -out {password}".format(**self.data))
        self._execute(command)

    # Encrypt the file with the random key
    def encrypt(self):
        command = path_expand(
            "openssl enc -aes-256-cbc -salt -in {file_in} -out {file_out} -pass file:{password}".format(**self.data))
        self._execute(command)


    # Encrypt the random key with the public keyfile
    def encryptPassword(self):
        command = path_expand(
            "openssl rsautl -encrypt -inkey {pem} -pubin -in {password} -out {password_enc}".format(**self.data))
        self._execute(command)


    def decryptRandomKey(self):
        command = path_expand(
            "openssl rsautl -decrypt -inkey  {key} -in {password_enc} -out {password_enc_plain}".format(**self.data))
        self._execute(command)


    def decrypt(self):
        command = path_expand(
            "openssl enc -d -aes-256-cbc -in {file_out} -out {file_out_plain} -pass file:{password_enc_plain}".format(**self.data))
        self._execute(command)

    def ssh_keygen(self):
        command = "ssh-keygen -t rsa -m pem"
        os.system(command)
        command = ""
        self.pem_create()

    def pem_create(self):
        command = path_expand("openssl rsa -in {key} -pubout  > {pem}".format(**self.data))

        # command = path_expand("openssl rsa -in id_rsa -pubout  > {pem}".format(**self.data))
        self._execute(command)
        command = "chmod go-rwx {key}.pem".format(**self.data)
        self._execute(command)

    def pem_verify(self):
        """
        this does not work
        :return:
        """
        if platform.system().lower() == 'darwin':
            command = "security verify-cert -c {pem}".format(**self.data)
            self._execute(command)

        command = "openssl verify  {pem}".format(**self.data)
        self._execute(command)


    def check_key(self, filename):
        error = False
        with open(self.data["key"]) as key:
            content = key.read()

        if "BEGIN RSA PRIVATE KEY" not in content:
            Console.error("Key is not a pure RSA key")
            error = True
        if "Proc-Type: 4,ENCRYPTED" in content and "DEK-Info:" not in content:
            Console.error("Key has no passphrase")
            error = True

        if error:
            Console.error("Key is not valid for cloudmesh")
            return False
        else:
            return True


    def set(self,filename, key, value):

        configDict = ConfigDict(filename)
        configDict[key]= value

    def edit(self):
        command = "vim {file_in}".format(**self.data)
        self._execute(command)

    def delete_folder(self):

        # delete the tmp folder
        path = '~/.cloudmesh/tmp'
        folder = os.path.exists(path)
        if folder:
            shutil.rmtree(path)


if __name__ == "__main__":
    '''
    for filename in ['file.txt', 'secret.txt']:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    # Creating a file with data

    with open("file.txt", "w") as f:
        f.write("Big Data is here.")
    '''
    e = EncryptFile('/Users/xiaoyue/Desktop/test.yaml', '/Users/xiaoyue/Desktop/test.yaml.enc','')
    e.decrypt()


    '''
    # if the file is existed
    file_in = "secret.txt"
    file_out = "plain.txt"
    # if the file is existed

    if not os.path.exists(file_in):
        os.system(r"touch {}".format(file_out))  # create the file
    
    '''

