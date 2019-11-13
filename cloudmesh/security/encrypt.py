import os
import platform
from base64 import b64encode
from getpass import getpass

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_private_key

"""
Functions to be replaced
1) EncryptFile.pem_verify()  
2) EncryptFile.check_passphrase()  
3) EncryptFile.check_key()  
4) EncryptFile.encrypt()  
5) EncryptFile.decrypt()  

Functions to be removed
1) EncryptFile.ssh_keygen()  
2) EncryptFile._execute()  
3) EncryptFile.pem_create()  
4) EncryptFile.pem_cat()  
"""
class CmsEncryptor:
    """ 
    Encrypts bytes for CMS
    I) key generation is outside scope of CmsEncryptor
      1) Generating 2048 bit RSA Private and Public PEM files
        A) Debian
            a) Ensure openssl is installed
            b) Execute: openssl genrsa -aes256 -out <priv_key_name>
            c) Execute: openssl rsa -in <priv_name> -outform PEM -pubout -out <pub_name>

      2) Generating 2048 bit RSA Private and Public SSH keys
        A) Debian
            a) ensure ssh-keygen is installed
            b) Execute: ssh-keygen -t rsa -m pem -f <base_priv_and_pub_name>

      2) Generating 384 bit ECC key
        A) Debian 
            a) TODO

    Replaces the following functions
        4) EncryptFile.encrypt()  
        5) EncryptFile.decrypt()  
    """        

    def __init__(self, debug=False):
        self.debug = debug
        self.tmp = path_expand("~/.cloudmesh/tmp")

    def getRandomBytes(self, len_bytes = 32):
        rand_bytes = os.urandom(len_bytes)
        return rand_bytes

    def getRandomInt(self, len_bytes = 32, order="big"):
        rb = self.getRandomBytes(len_bytes)
        rand_int = int.from_bytes(rb, byteorder=order)
        return rand_int

    def encrypt_rsa(self, pub = None, pt = None, padding="OAEP"):
        if pub is None:
            Console.error("empty key argument")

        if pt is None:
            Console.error("attempted to encrypt empty data")

        pad = None
        if padding == "OAEP":
            pad = padding.OAEP(
                    mfg = padding.MFG1( algorithm = hashes.SHA256()),
                    algorithm = hashes.SHA256(),
                    label = None)
        elif padding == "PKCS":
            pad = padding.PKCS1v15
        else:
            Console.error("Unsupported padding scheme")

        return pub.encrypt(pt, pad)

    def decrypt_rsa(self, priv = None, ct = None, padding="OAEP"):
        if priv is None:
            Console.error("empty key arugment")
        if ct is None:
            Console.error("attempted to decrypt empty data")
        pad = None
        if padding == "OAEP":
            pad = padding.OAEP(
                    mfg = padding.MFG1( algorithm = hashes.SHA256() ),
                    algorithm = hashes.SHA256(),
                    label = None )
        elif padding == "PKCS":
            pad = padding.PKCS1v15
        else:
            Console.error("Unsupported padding scheme")

        return priv.decrypt( ct, pad )
            
                
    def decrypt_aesgcm(self, key=None, nonce=None, aad=None, ct=None):
        aesgcm = AESGCM(key)
        pt = aesgcm.decrypt(nonce, ct, aad)
        return pt

    def encrypt_aesgcm(self, data = None, aad = None):
        """
        @param: bytes: the plaintext data 
        @param: bytes: the additional authenticated data (can be public)
        @return: 
            - bytes: AESGCM key object
            - bytes: nonce (random data)
            - bytes: ciphertext
        """
        if data is None:
            Console.error("Attempted to encrypt empty data")

        # ALWAYS generate a new nonce. 
        # ALL security is lost if same nonce and key are used with diff text 
        nonce = self.getRandomBytes(12)
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        ct = aesgcm.encrypt(nonce, data, aad)

        return key, nonce, ct

class CmsHasher:
    def __init__(self, data = None, data_type = str):
        #Check if data is empty
        if data is not None:
            # Ensure proper data type
            if data_type is str:
                self.data = data.encode()
            elif data_type is bytes:
                self.data = data
            else:
                Console.error("data_type not supported")

    def hash_data(self, data = None, hash_alg="SHA256"
                    , encoding = False, clean = False):
        digest = None
        if hash_alg == "MD5":
            # !!!!!!!!!!!!!!!!!!!!!!! Warning !!!!!!!!!!!!!!!!!!!!!!!!
            # This hash has know vulnerabilities. 
            # ONLY used this when the data does not need to be secert. 
            # !!!!!!!!!!!!!!!!!!!!!!! Warning !!!!!!!!!!!!!!!!!!!!!!!!
            digest = hashes.Hash(hashes.MD5(), backend = default_backend())
        else:
            Console.error("Unsupported Hashing algorithm")
        if type(data) is str:
            data = data.encode()
        digest.update(data)
        hashed = digest.finalize()

        # Encode data if requested
        if encoding == False:
            """no op, just for check"""
        elif encoding == "b64":
            hashed = b64encode(hashed).decode()
        else:
            Console.error("Unknown encoding requested")

        # Clean data for system purposes if requested
        if clean:
            remove_chars = ['+','=','\\','/'] #special dir chars on typical os
            for char in remove_chars:
                if char in hashed:
                    hashed = hashed.replace(char, "")

        return hashed 
            

class KeyHandler:
    def __init__(self, debug=False, priv=None, pub=None, pem=None):
        ### CMS debug parameter
        self.debug = debug
        ### pyca Key Objects
        self.priv = priv
        self.pub = pub
        self.pem = pem

    def new_rsa_key(self, byte_size = 2048, pwd=None):
        """
        @param: int: size of key in bytes
        @param: str: password for key
        return: bytes of private RSA key
        """
        self.priv = rsa.generate_private_key(
            public_exponent = 65537, # do NOT change this!!!
            key_size = byte_size,
            backend=default_backend()
        )

        # Calculate public key
        self.pub = self.priv.public_key()

        # Serialize the key
        return self.serialize_key(key_type = "PRIV", password = pwd)

    def get_pub_key_bytes(self, encoding="PEM", format="SubjectInfo"):
        if self.pub is None:
            if self.priv is None:
                Console.error("Key data is empty")
            else:
                self.pub = self.priv.public_key()
        else:
            return self.serialize_key(key=self.pub, key_type = "PUB", 
                                    encoding = encoding, format = format)

    def serialize_key(self, debug=False, key=None, key_type=None, encoding="PEM", 
                      format="PKCS8", password=None):
        """
        @param: bool:       cloudmesh debug flag
        @param: key_object: pyca key object
        @param: str:        the type of key file [PRIV, PUB]
        @param: str:        the type of encoding [PEM, SSH]
        @param: str:        private [PKCS8, OpenSSL], Public [SubjectInfo, SSH]
        @param: str:        password for key (Private keys only)
        return:             serialized key bytes
        """
        #TODO: add try-catching
        # Ensure the key is initialized
        if key is None:
            if key_type == "PRIV":
                if self.priv is None:
                    Console.error("No key given")
                else:   
                    key = self.priv
            elif key_type == "PUB":
                if self.pub is None:
                    Console.error("No key given")
                else:
                    key = self.pub
            else:
                Console.error("No key given")

        # Discern formating based on if key is public or private
        key_format = None
        if key_type == "PRIV":
            key_format = serialization.PrivateFormat
        elif key_type == "PUB":
            key_format = serialization.PublicFormat
        else: 
            Console.error("key needs to be PRIV or PUB")
            
        # Discern formatting of key
        if key_type == "PRIV":
            if format == "PKCS8":
                key_format = key_format.PKCS8
            elif format == "OpenSSL":
                key_format = key_format.TraditionalOpenSSL
            else:
                Console.error("Unsupported private key format")
        elif key_type == "PUB":
            if format == "SubjectInfo":
                key_format = key_format.SubjectPublicKeyInfo
            elif format == "SSH":
                key_format = key_format.OpenSSH
            else:
                Console.error("Unsupported public key format")

        # Discern encoding
        encode = None
        if encoding == "PEM":
            encode = serialization.Encoding.PEM
        elif encoding == "SSH":
            encod = serialization.Encoding.OpenSSH
        else:
            Console.error("Unsupported key encoding")
            
        # Discern encryption algorithm (Private keys only)
        # This also assigns the password if given
        enc_alg = None
        if key_type == "PRIV":
            if password is None:
                enc_alg = serialization.NoEncryption()
            else:
                pwd = str.encode(password)
                enc_alg = serialization.BestAvailableEncryption(pwd)

        # Serialize key
        sk = None
        if key_type == "PUB":
            sk = key.public_bytes( encoding = encode, format = key_format)
        elif key_type == "PRIV":
            sk = key.private_bytes(encoding = encode, format = key_format,
                                   encryption_algorithm = enc_alg)
        return sk
            
class PemHandler:
    """ 
    Responsible for loading and verify PEM files

    replaces following functions:
        1) EncryptFile.check_key
        1) EncryptFile.check_passphares
        1) EncryptFile.pem_verify
    """
    def __init__(self, debug=False):
        self.debug = debug
        self.data = b""

    def read_file_bytes(self, input_path=""):
        #TODO: add try catch for input_path (ensure its not empty)
        path = path_expand(input_path)
        if self.debug:
            Console.ok( f"Opening file: {path}" )
        in_file = open(path, "rb")
        data = in_file.read()
        in_file.close()
        return data
            
    def load_private_pem_bytes(self, input_path="", pwd=None):
        """
        @param: str: path to file being loaded
        @param: bytes: password bytes to unlock pem file
        """
        pem_data = self.read_file_bytes(input_path)
        try:
            key = load_pem_private_key(pem_data,
                    password = pwd,
                    backend = default_backend())

            # Currently only RSA keys are supported
            if isinstance (key, rsa.RSAPrivateKey):
                k = KeyHandler(priv=key)
                sk = k.serialize_key(key_type="PRIV")
                return sk
            else:
                raise TypeError
        except ValueError as e:
            Console.Error("Pem file could not be read")
        except TypeError as e:
            Console.Error("Must use RSA private keys")
        except cyptorgaphy.exceptions.UnSupportedAlgorithm as e:
            Console.error(e)

#BUG: TODO: usage of path_expand is compleyely wrong

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
