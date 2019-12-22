from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters


# see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/NetworkCommand.py


class IpCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_ip(self, args, arguments):
        """
        ::

            Usage:
                ip list  [--cloud=CLOUD] [--output=OUTPUT]
                ip create [N] [--cloud=CLOUD]
                ip delete [IP] [--cloud=CLOUD]
                ip attach [NAME] [IP]
                ip detach [NAME] [IP]


            Options:
                -h                          help message
                --cloud=CLOUD               Name of the cloud
                --output=OUTPUT             The output format [default: table]

            Arguments:
                N         Number of IPS to create
                IP        IP Address
                NAME      Name of the service


            Description:
                ip list floating [--cloud=CLOUD] [--output=OUTPUT]
                    returns a list of all the floating IPS in the cloud

                ip add floating [--cloud=CLOUD]
                    adds a floating ip to the pool of available floating ips

                ip delete floating [IP] [--cloud=CLOUD]
                    deletes a floating ip to the pool of available
                    floating ips

                ip add NAME [IP]
                    add the ip to the named vm

                ip delete NAME [IP]
                    deletes the ip from the vm

        """

        def get_ip(ip):

            if ip is None:
                # find a free one
                try:
                    ip = provider.find_available_public_ip()
                    return ip
                except Exception as e:
                    Console.error("No free floating ip found")
                    return ""

        map_parameters(arguments,
                       "cloud",
                       "output")
        arguments.vm = arguments.NAME

        variables = Variables()

        if arguments.list:

            cloud = Parameter.find("cloud", arguments, variables)

            print(f"cloud {cloud}")
            provider = Provider(name=cloud)
            ips = provider.list_public_ips()

            provider.Print(ips, output=arguments.output, kind="ip")

        elif arguments.create:

            cloud = Parameter.find("cloud", arguments, variables)

            n = arguments.N or 1

            print(f"cloud {cloud}")
            provider = Provider(name=cloud)

            for i in range(0, int(n)):
                ips = provider.create_public_ip()
            ips = provider.list_public_ips()

            provider.Print(ips, output=arguments.output, kind="ip")


        elif arguments.delete:

            cloud = Parameter.find("cloud", arguments, variables)

            print(f"cloud {cloud}")
            provider = Provider(name=cloud)

            ip = arguments.IP

            ip = get_ip(arguments.IP)

            ips = provider.delete_public_ip(ip)
            ips = provider.list_public_ips()

            provider.Print(ips, output=arguments.output, kind="ip")

        elif arguments.attach:

            name = Parameter.find("vm", arguments, variables)
            cm = CmDatabase()
            vm = cm.find_name(name, kind="vm")[0]
            cloud = vm["cm"]["cloud"]

            print(f"cloud {cloud}")
            provider = Provider(name=cloud)

            ip = get_ip(arguments.IP)
            try:
                ips = provider.attach_public_ip(name=name, ip=ip)
            except Exception as e:
                print(e)
                Console.error("Could not assign public ip.")


        elif arguments.detach:
            name = Parameter.find("vm", arguments, variables)
            cm = CmDatabase()
            vm = cm.find_name(name, kind="vm")[0]
            cloud = vm["cm"]["cloud"]

            print(f"cloud {cloud}")
            provider = Provider(name=cloud)
            ip = provider.get_public_ip(name=name)

            print(name, ip)

            try:
                ips = provider.detach_public_ip(name=name, ip=ip)
            except Exception as e:
                print(e)
                Console.error("can not detach ip")
