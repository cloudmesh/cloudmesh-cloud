from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.compute.libcloud.Provider import Provider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
from cloudmesh.management.configuration.SSHkey import SSHkey

# nosetest -v --nopature
# nosetests -v --nocapture tests/test_key.py

class TestName:

    def setup(self):
        self.sshkey = SSHkey()


    def test_01_key(self):
        HEADING()
        pprint(self.sshkey)
        print(self.sshkey)

        print(type(self.sshkey))


        pprint(self.sshkey.__dict__)


        #pprint(sshkey.key)


        #print("Fingerprint:", sshkey.fingerprint)
        #pprint(sshkey.__key__)
        #print("sshkey", sshkey)
        #print("str", str(sshkey))
        #print(sshkey.type)
        #print(sshkey.__key__['key'])
        #print(sshkey.key)
        #print(sshkey.comment)
        """
        key1 = "ssh-rsa abcdefg comment"
        key2 = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDD+NswLi/zjz" + \
                "7Vf575eo9iWWku5m4nVSPMgP13JbKCTVKtavAXt8UPZTkYVWi" + \
                "USeXRqlf+EZM11U8Mq6C/P/ECJS868rn2KSwFosNPF0OOz8zm" + \
                "TvBQShtvBBBVd1kmZePxFGviZbKwe3z3iATLKE8h7pwcupqTi" + \
                "n9m3FhQRsGSF7YTFcGXv0ZqxFA2j9+Ix7SVbN5IYxxgwc+mxO" + \
                "zYIy1SKEAOPJQFXKkiXxNdLSzGgjkurhPAIns8MNYL9usKMGz" + \
                "hgp656onGkSbQHZR3ZHsSsTXWP3SV5ih4QTTFunwB6C0TMQVs" + \
                "EGw1P49hhFktb3md+RC4DFP7ZOzfkd9nne2B mycomment"
        print(key_validate("string", key1))
        print(key_validate("string", key2))
        print(key_parse(key1))
        print(key_parse("abcdedfg"))
        print(key_parse("ssh-rsa somestringhere")[2])
        """


    def test_02_git(self):
        HEADING()
        config = Config()
        username = config["cloudmesh.profile.github"]
        print ("Username:", username)
        keys = self.sshkey.get_from_git(username)
        pprint (keys)
        print(Printer.flatwrite(keys,
                            sort_keys=("name"),
                            order=["name", "fingerprint"],
                            header=["Name", "Fingerprint"])
              )


class other:
    def test_01_list_keys(self):
        HEADING()
        keys = self.p.keys()
        pprint(keys)

        print(Printer.flatwrite(keys,
                            sort_keys=("name"),
                            order=["name", "fingerprint"],
                            header=["Name", "Fingerprint"])
              )

