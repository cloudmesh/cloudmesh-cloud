from __future__ import print_function
import base64
import hashlib
import struct
from os.path import basename
from cloudmesh.common.util import path_expand
from pathlib import Path
import requests

from cloudmesh.management.configuration.config import Config


# noinspection PyBroadException
class SSHkey(dict):

    def __init__(self):
        self.load()

    def load(self):
        self["profile"] = Config()["cloudmesh"]["profile"]
        self["path"] = path_expand(self["profile"]["publickey"])

        self["uri"] = 'file://{path}'.format(path=self["path"])
        self['string'] = open(Path(self["path"]), "r").read().rstrip()

        (self['type'],
         self['key'],
         self['comment']) = SSHkey._parse(self['string'])

        self['fingerprint'] = SSHkey._fingerprint(self['string'])
        self["name"] = basename(self["path"]).replace(".pub", "").replace("id_", "")

        self['comment'] = self['comment']
        self['source'] = 'ssh'

    def set_permissions(self, path):
        """
        Sets the permissions of the path assuming the path is a public or private key
        :param path:
        :return:
        """
        # TODO: implement
        # use python os.chmod
        # work with students that do windows and find out how to do it in windows also
        pass

    # noinspection PyDictCreation
    def get_from_git(self, user, keyname=None):
        """
        gets the key from github

        :param keyname: the keyname
        :param user: the github username
        :return: an array of public keys
        :rtype: list
        """
        uri = "https://api.github.com/users/{user}/keys".format(user=user)

        content = requests.get(uri).json()

        d = []

        for id in range(0, len(content)):
            entry = content[id]
            key = entry['key']
            thekey = {}

            name = "{user}_git_{id}".format(user=user, id=id)

            thekey = {
                'id': id,
                'uri': uri,
                'string': key,
                'fingerprint': SSHkey._fingerprint(key),
                'name': name,
                'comment': name,
                'cm_id': name,
                'source': 'git',
                'kind': 'key'
            }

            thekey["type"], thekey["key"], thekey["comment"] = SSHkey._parse(
                key)

            if thekey["comment"] is None:
                thekey["comment"] = name
            d.append(thekey)
        return d

    def __str__(self):
        return self['string']

    @property
    def fingerprint(self):
        return self['fingerprint']

    @property
    def type(self):
        return self['type']

    @property
    def comment(self):
        return self['comment']

    @classmethod
    def _fingerprint(cls, entirekey):
        """returns the fingerprint of a key.
        :param entirekey: the key
        :type entirekey: string
        """
        t, keystring, comment = cls._parse(entirekey)
        if keystring is not None:
            return cls._key_fingerprint(keystring)
        else:
            return ''

    @classmethod
    def _key_fingerprint(cls, key_string):
        """create the fingerprint form just the key.

        :param key_string: the key
        :type key_string: string
        """
        # key = base64.decodestring(key_string)
        # fp_plain = hashlib.md5(key).hexdigest()
        key_padding = key_string.strip() + '=' * (4 - len(key_string.strip()) % 4)
        key = base64.b64decode(key_padding.encode('ascii'))
        fp_plain = hashlib.md5(key).hexdigest()

        return ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))

    @classmethod
    def _parse(cls, keystring):
        """
        parse the keystring/keycontent into type,key,comment
        :param keystring: the content of a key in string format
        """
        # comment section could have a space too
        keysegments = keystring.split(" ", 2)
        keytype = keysegments[0]
        key = None
        comment = None
        if len(keysegments) > 1:
            key = keysegments[1]
            if len(keysegments) > 2:
                comment = keysegments[2]
        return keytype, key, comment

    def _validate(self, keytype, key):
        """reads the key string from a file. THIS FUNCTION HAS A BUG.

        :param key: either the name of  a file that contains the key, or the entire contents of such a file
        :param keytype: if 'file' the key is read form the file specified in key.
                        if 'string' the key is passed as a string in key
        """
        keystring = None
        if keytype.lower() == "file":
            try:
                keystring = open(key, "r").read()
            except Exception as e:
                return False
        elif keytype.lower() == "string":
            keystring = key

        try:

            keytype, key_string, comment = self._parse(keystring)
            data = base64.decodebytes(key_string)
            int_len = 4
            str_len = struct.unpack('>I', data[:int_len])[0]
            # this should return 7

            if data[int_len:int_len + str_len] == keytype:
                return True
        except Exception as e:
            # print(e)
            return False

    def _keyname_sanitation(self, username, keyname):
        keynamenew = "{username}_{keyname}".format(
            username=username,
            keyname=keyname.replace('.', '_').replace('@', '_'))
        return keynamenew

