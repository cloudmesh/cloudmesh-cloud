from cloudmesh.common.Shell import Shell

class Shell(Shell):
    @staticmethod
    def check(args):
        """
        check a vm

        :param args: dict of {keypath, username, dest(ip or dns)}
        :return: a dict representing the result, if ret_code=0 ping is successfully
        """
        key = args['key']
        location = args['username'] + '@' + args['host']
        command = ['ssh',
                   "-o", "StrictHostKeyChecking=no",
                   "-o", "UserKnownHostsFile=/dev/null",
                   '-i', key, location, 'uname -a']
        ret_code = subprocess.run(command, capture_output=False).returncode
        if ret_code == 0:
            Console.ok(args['host'] + '\t...ok')
        else:
            Console.error(args['host'] + '\t...error')
        return {args['host']: ret_code}

    @classmethod
    def checks(cls, key=None, username=None, hosts=None, processors=3):
        """
        checks a list of given vms

        :param ips: a list of ip addresses
        :param count: number of pings to run per ip
        :param processors: number of processors to Pool
        :return: list of dicts representing the ping result
        """
        # wrap ip and count into one list to be sent to Pool map
        args = [{'key':key, 'username':username, 'host':host} for host in hosts]

        with Pool(processors) as p:
            res = p.map(Shell.check, args)
        return res

    @staticmethod
    def ping_ip(args):
        """
        ping a vm

        :param args: dict of {ip address, count}
        :return: a dict representing the result, if ret_code=0 ping is successfully
        """
        ip = args['ip']
        count = str(args['count'])
        param = '-n' if platform=='windows' else '-c'
        command = ['ping', param, count, ip]
        ret_code = subprocess.run(command, capture_output=False).returncode
        if ret_code == 0:
            Console.ok(ip + '\t...ok')
        else:
            Console.error(ip + '\t...error')
        return {ip: ret_code}

    @classmethod
    def pings(cls, ips=None, count=1, processors=3):
        """
        ping a list of given ip addresses

        :param ips: a list of ip addresses
        :param count: number of pings to run per ip
        :param processors: number of processors to Pool
        :return: list of dicts representing the ping result
        """
        # wrap ip and count into one list to be sent to Pool map
        args = [{'ip':ip, 'count':count} for ip in ips]

        with Pool(processors) as p:
            res = p.map(Shell.ping_ip, args)
        return res

def main():
    """
    a test that should actually be added into a nosetest
    :return:
    """
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


if __name__ == "__main__":
    main()
