from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class IpCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/NetworkCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_ip(self, args, arguments):
        """
        ::

            Usage:
                ip list floating [--cloud=CLOUD] [--output=OUTPUT]
                ip add floating [--cloud=CLOUD]
                ip delete floating [IP] [--cloud=CLOUD]
                ip add NAME [IP]
                ip delete NAME


            Options:
                -h                          help message
                --cloud=CLOUD               Name of the IaaS cloud e.g. india_openstack_grizzly.

            Arguments:
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

        print(arguments)

        # m = Manager()

        # if arguments.FILE:
        #    print("option a")
        #    m.list(arguments.FILE)

        # elif arguments.list:
        #    print("option b")
        #    m.list("just calling list without parameter")
