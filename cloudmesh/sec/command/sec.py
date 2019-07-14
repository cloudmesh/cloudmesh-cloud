from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.secgroup.Secgroup import Secgroup, SecgroupRule
from pprint import pprint
from cloudmesh.common.Printer import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.secgroup.Secgroup import SecgroupExamples
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.compute.vm.Provider import Provider

class SecCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/master/cloudmesh_client/shell/plugins/SecgroupCommand.py
    # noinspection PyUnusedLocal
    @command
    def do_sec(self, args, arguments):
        """
        ::

            Usage:
                sec rule list --cloud=CLOUDS [--output=OUTPUT]
                sec rule list --name=RULES [--output=OUTPUT]
                sec rule list [--output=OUTPUT]
                sec rule add RULE FROMPORT TOPORT PROTOCOL CIDR
                sec rule delete GROUP [--cloud=CLOUD]
                sec group list --cloud=CLOUDS [--output=OUTPUT]
                sec group list [--name=GROUPS] [--output=OUTPUT]
                sec group add GROUP RULES DESCRIPTION
                sec group delete GROUP [--cloud=CLOUD]
                sec group load [GROUP] [--cloud=CLOUD]
                sec list [--output=OUTPUT]
                sec load
                sec clear

            Options:
                --output=OUTPUT Specify output format, in one of the following:
                                table, csv, json, yaml, dict
                                [default: table].
                --cloud=CLOUD   Name of the IaaS cloud e.g. kilo,chameleon.
                                The clouds are defined in the yaml file.
                                If the name "all" is used for the cloud all
                                clouds will be selected.
            Arguments:
                RULE          The security group rule name
                GROUP         The label/name of the security group
                FROMPORT      Staring port of the rule, e.g. 22
                TOPORT        Ending port of the rule, e.g. 22
                PROTOCOL      Protocol applied, e.g. TCP,UDP,ICMP
                CIDR          IP address range in CIDR format, e.g.,
                              129.79.0.0/16

            Examples:
                sec group list
                sec group list --cloud=kilo
                sec group add my_new_group webapp 8080 8080 tcp 0.0.0.0/0
                seg group delete my_group my_rule
                sec group delete my_unused_group --cloud=kilo
                sec group upload --cloud=kilo

            Description:

                THIS IS OUTDATED

                security_group command provides list/add/delete
                security_groups for a tenant of a cloud, as well as
                list/add/delete of rules for a security group from a
                specified cloud and tenant.
                Security groups are first assembled in a local database.
                Once they are defined they can be added to the clouds.
                sec group list [--output=OUTPUT]
                    lists all security groups and rules in the database
                sec group list GROUP [--output=OUTPUT]
                    lists a given security group and its rules defined
                    locally in the database
                sec group list --cloud=CLOUD [--output=OUTPUT]
                    lists the security groups and rules on the specified clouds.
                sec group add GROUP RULE FROMPORT TOPORT PROTOCOL CIDR
                    adds a security rule with the given group and the details
                    of the security rules
                sec group delete GROUP [--cloud=CLOUD]
                    Deletes a security group from the local database. To make
                    the change on the remote cloud, using the 'upload' command
                    afterwards.
                    If the --cloud parameter is specified, the change would be
                    made directly on the specified cloud
                sec group delete GROUP RULE
                    deletes the given rule from the group. To make this change
                    on the remote cloud, using 'upload' command.
                sec group upload [GROUP] [--cloud=CLOUD...]
                    uploads a given group to the given cloud. If the cloud is
                    not specified the default cloud is used.
                    If the parameter for cloud is "all" the rules and groups
                    will be uploaded to all active clouds.
                    This will synchronize the changes (add/delete on security
                    groups, rules) made locally to the remote cloud(s).
                    groups, rules) made locally to the remote cloud(s).
        """

        map_parameters(arguments,
                       'cloud',
                       'output',
                       'name')

        rules = SecgroupRule()
        groups = Secgroup()

        def Print(kind, list):
            print(Printer.write(list,
                            sort_keys=groups.output[kind]['sort_keys'],
                            order=groups.output[kind]['order'],
                            header=groups.output[kind]['header'],
                            output=arguments.output))

        def list_all():
            data = []

            group_entries = groups.list()

            for group_entry in group_entries:
                group_name = group_entry['name']

                for rule_name in group_entry['rules']:
                    try:
                        rule_entry = rules.list(name=rule_name)[0]
                        rule_entry['rule'] = rule_name
                        rule_entry['group'] = group_name
                        data.append(rule_entry)
                    except:
                        pass
            Print("all", data)

        if arguments.group and arguments.list and arguments.cloud:

            clouds = Parameter.expand(arguments.cloud)

            if len(clouds) == 0:
                variables = Variables()
                cloudname = variables['cloud']
                clouds = [cloudname]
            keys = []

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                cloud_groups = provider.list_secgroups()

            Print("group", cloud_groups)

            return ""

        elif arguments.rule and arguments.list and arguments.cloud:

            clouds = Parameter.expand(arguments.cloud)

            if len(clouds) == 0:
                variables = Variables()
                cloudname = variables['cloud']
                clouds = [cloudname]
            keys = []

            for cloud in clouds:
                print(f"cloud {cloud}")
                provider = Provider(name=cloud)
                cloud_rules = provider.list_secgroups_rules()

            Print("rule", cloud_rules)

            return ""

        elif arguments.group and arguments.list:
            found = groups.list()
            for entry in found:
                group_rules = entry['rules']
                if type(group_rules) == list:
                    entry['rules'] = ', '.join(group_rules)
            Print("group", found)

        elif arguments.rule and arguments.list:
            found = rules.list()
            Print("rule", found)


        elif arguments.rule and arguments.add:
            rules = SecgroupRule()
            rules.add(
                arguments.GROUP,
                arguments.RULE,
                arguments.FROMPORT,
                arguments.TOPORT,
                arguments.PROTOCOL,
                arguments.CIDR,
            )

        elif arguments.group and arguments.list:
            secgroup = Secgroup()
            group = secgroup.list(arguments.GROUP)

            pprint (group)


        elif arguments.list:

            list_all()

        elif arguments.load:

              examples = SecgroupExamples()
              examples.load()
              list_all()

        elif arguments.clear:

            groups.clear()
            rules.clear()


        return ""
