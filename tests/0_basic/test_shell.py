###############################################################
# pytest -v --capture=no tests/0_basic/test_shell.py
# pytest -v  tests/0_basic/test_shell.py
# pytest -v --capture=no  tests/0_basic/test_shell.py:Test_name.<METHIDNAME>
###############################################################
from pprint import pprint
from cloudmesh.common.util import HEADING
from cloudmesh.management.configuration.name import Name
import pytest
import os
from cloudmesh.common.util import path_expand
from cloudmesh.common3.Shell import Shell


@pytest.mark.incremental
class TestName:

    def test_shell(self):

        shell = Shell()

        print(shell.terminal_type())

        r = shell.execute('pwd')  # copy line replace
        print(r)

        # shell.list()

        # print json.dumps(shell.command, indent=4)

        # test some commands without args
        """
        for cmd in ['whoami', 'pwd']:
            r = shell._execute(cmd)
            print ("---------------------")
            print ("Command: {:}".format(cmd))
            print ("{:}".format(r))
            print ("---------------------")
        """
        r = shell.execute('ls', ["-l", "-a"])
        print(r)

        r = shell.execute('ls', "-l -a")
        print(r)

        r = shell.ls("-aux")
        print(r)

        r = shell.ls("-a", "-u", "-x")
        print(r)

        r = shell.pwd()
        print(r)

