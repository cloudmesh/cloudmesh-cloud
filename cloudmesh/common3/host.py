import subprocess
from multiprocessing import Pool
from sys import platform

from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter


class Host(object):

    @staticmethod
    def _check(args):
        """
        check a vm

        :param args: dict of {keypath, username, dest(ip or dns)}
        :return: a dict representing the result, if ret_code=0 ping is successfully
        """
        key = args['key']
        host = args['host']
        username = args['username']

        location = f"{username}@{host}"
        command = ['ssh',
                   "-o", "StrictHostKeyChecking=no",
                   "-o", "UserKnownHostsFile=/dev/null",
                   '-i', key, location, 'uname -a']
        ret_code = subprocess.run(command, capture_output=False).returncode
        if ret_code == 0:
            Console.ok(f"{host}  ... ok")
        else:
            Console.error(f"{host}  ... could not login")
        return {host: ret_code}

    @staticmethod
    def check(hosts=None, username=None, key="~/.ssh/id_ras.pub", processors=3):
        #
        # BUG: this code has a bug and does not deal with different usernames on the host to be checked.
        #
        """

        :param hosts: a list of hosts to be checked
        :param username: the usernames for the hosts
        :param key: the key for logging in
        :param processors: the number of parallel checks
        :return: list of dicts representing the ping result
        """

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

        # wrap ip and count into one list to be sent to Pool map
        args = [{'key': key, 'username': username, 'host': host} for host in hosts]

        with Pool(processors) as p:
            res = p.map(Host._check, args)
        return res

    @staticmethod
    def _ping(args):
        """
            ping a vm

            :param args: dict of {ip address, count}
            :return: a dict representing the result, if ret_code=0 ping is successfully
            """
        ip = args['ip']
        count = str(args['count'])
        count_flag = '-n' if platform == 'windows' else '-c'
        command = ['ping', count_flag, count, ip]
        ret_code = subprocess.run(command, capture_output=False).returncode
        if ret_code == 0:
            Console.ok(f"{ip} ... ok")
        else:
            Console.error(f"{ip} ... error")
        return {ip: ret_code}

    @staticmethod
    def ping(hosts=None, count=1, processors=3):
        """
        ping a list of given ip addresses

        :param ips: a list of ip addresses
        :param count: number of pings to run per ip
        :param processors: number of processors to Pool
        :return: list of dicts representing the ping result
        """

        # first expand the ips to a list

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

            # wrap ip and count into one list to be sent to Pool map
        args = [{'ip': ip, 'count': count} for ip in hosts]

        with Pool(processors) as p:
            res = p.map(Host._ping, args)

        return res
