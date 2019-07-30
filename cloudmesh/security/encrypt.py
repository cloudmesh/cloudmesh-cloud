import os
import platform
from getpass import getpass

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand


# security import ~/.ssh/id_rsa_.pem -k ~/Library/Keychains/login.keychain

# $ brew install openssl
# $ brew link openssl --force
# brew install openssh --with-libressl

class EncryptFile(object):
    """

    keys must be generated with

        ssh-keygen -t rsa -m pem
        openssl rsa -in id_rsa -out id_rsa.pem

    """

    # noinspection PyShadowingNames
    def __init__(self, filename, secret):
        self.data = dotdict({
            'file': filename,
            'secret': secret,
            'pem': path_expand('~/.ssh/id_rsa.pem'),
            'key': path_expand('~/.ssh/id_rsa')
        })
        if not os.path.exists(self.data["pem"]):
            self.pem_create()

    def ssh_keygen(self):
        command = "ssh-keygen -t rsa -m pem"
        os.system(command)
        self.pem_create()

    # noinspection PyShadowingNames,PyShadowingNames
    def check_key(self, filename=None):
        if filename is None:
            filename = self.data["key"]
        error = False
        with open(filename) as key:
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

    # noinspection PyMethodMayBeStatic
    def _execute(self, command):
        os.system(command)

    # noinspection PyPep8,PyBroadException
    def check_passphrase(self):
        """
        this does not work with pem

        checks if the ssh key has a password
        :return:
        """

        self.data["passphrase"] = getpass("Passphrase:")

        if self.data.passphrase is None or self.data.passphrase == "":
            Console.error("No passphrase specified.")
            raise ValueError('No passphrase specified.')

        try:
            command = "ssh-keygen -p -P {passphrase} -N {passphrase} -f {key}".format(
                **self.data)
            r = Shell.execute(command, shell=True, traceflag=False)

            if "Your identification has been saved with the new passphrase." in r:
                Console.ok("Password ok.")
                return True
        except:
            Console.error("Password not correct.")

        return False

    def pem_verify(self):
        """
        this does not work
        :return:
        """
        if platform.system().lower() == 'darwin':
            command = "security verify-cert -c {key}.pem".format(**self.data)
            self._execute(command)

        command = "openssl verify  {key}.pem".format(**self.data)
        self._execute(command)

    def pem_create(self):
        command = path_expand(
            "openssl rsa -in {key} -pubout  > {pem}".format(**self.data))

        # command = path_expand("openssl rsa -in id_rsa -pubout  > {pem}"
        # .format(**self.data))
        self._execute(command)
        command = "chmod go-rwx {key}.pem".format(**self.data)
        self._execute(command)

    # openssl rsa -in ~/.ssh/id_rsa -out ~/.ssh/id_rsa.pem
    # TODO: BUG
    #
    def pem_cat(self):
        command = path_expand("cat {pem}".format(**self.data))
        self._execute(command)

    def encrypt(self):
        # encrypt the file into secret.txt
        print(self.data)
        command = path_expand(
            "openssl rsautl -encrypt -pubin "
            "-inkey {key}.pem -in {file} -out {secret}".format(**self.data))
        self._execute(command)

    # noinspection PyShadowingNames
    def decrypt(self, filename=None):
        if filename is not None:
            self.data['secret'] = filename

        command = path_expand(
            "openssl rsautl -decrypt "
            "-inkey {key} -in {secret} -out {file}".format(**self.data))
        self._execute(command)


if __name__ == "__main__":

    for filename in ['file.txt', 'secret.txt']:
        # noinspection PyBroadException
        try:
            os.remove(filename)
        except Exception as e:
            pass

    # Creating a file with data

    with open("file.txt", "w") as f:
        f.write("Big Data is here.")

    e = EncryptFile('file.txt', 'secret.txt')
    e.encrypt()
    e.decrypt()
