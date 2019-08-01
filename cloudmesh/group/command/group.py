from pprint import pprint

from cloudmesh.common.Printer import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.group.Group import Group
# from cloudmesh_client.cloud.group import Group
# rom cloudmesh_client.default import Default
# from cloudmesh_client.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class GroupCommand(PluginCommand):

    @command
    def do_group(self, args, arguments):
        """
        ::

            Usage:
                group list [GROUPNAME] [--format=FORMAT]
                group remove NAMES [--group=GROUPNAME]
                group add NAMES [--type=TYPE] [--group=GROUPNAME] [--format=FORMAT]
                group delete GROUPS
                group copy FROM TO
                group merge GROUPA GROUPB MERGEDGROUP

            manage the groups

            Arguments:

                NAMES        names of object to be added
                GROUPS       names of a groups
                FROM         name of a group
                TO           name of a group
                GROUPA       name of a group
                GROUPB       name of a group
                MERGEDGROUP  name of a group

            Options:
                --format=FORMAT     the output format [default: table]
                --type=TYPE         the resource type
                --name=NAME         the name of the group
                --id=IDS            the ID(s) to add to the group


            Description:

                cloudmesh can manage groups of resources. Operations can be
                performed on these groups including termination of services that
                are registered with the group.

                A default group can be set with the command

                  cms set group=GROUPNAME

                where GROUPNAME is the group to which all future resources be
                added. The group can also be set as part of other commands with
                the --group=GROUPNAME option.


            Example:
                set group=mygroup

                group add --type=vm --id=albert-[001-003]
                    adds the vms with the given name using the Parameter
                    see base

                group add --type=vm
                 adds the last vm to the group

                group delete --name=mygroup
                    deletes all objects in the group
        """
        # pprint(arguments)

        order = [
            'cm.group',
            'cm.name',
            'cm.kind',
            'cm.status',
            'cm.modified',
            'cm.created']

        header = [
            'Group',
            'Name',
            'Kind',
            'Status',
            'Modified',
            'Created']

        if arguments.add:

            # "group add NAMES [--type=TYPE] [--group=GROUPNAME]"
            #
            # tod doe not yet search for type = kind
            #
            names = Parameter.expand(arguments.NAMES)
            group = arguments["--group"] or "default"

            g = Group()
            entry = g.add(services=names, group=group)

            pprint(entry)

            print(Printer.flatwrite(entry,
                                    order=order,
                                    header=header,
                                    output=arguments["--format"]))

        elif arguments.list:

            # group list [GROUPNAME] [--format=FORMAT]

            group = arguments.GROUPNAME or "default"

            g = Group()
            entry = g.list(group=group)

            if arguments["--format"] == "list":
                pprint(entry)
            else:
                print(Printer.flatwrite(entry,
                                        order=order,
                                        header=header,
                                        output=arguments["--format"]))

        """
    

        elif arguments["delete"]:
            groups = Parameter.expand(arguments["GROUPS"])

            for group in groups:
                result = Group.delete(group)

                if result:
                    Console.ok(result)
                else:
                    Console.error(
                        "delete group {}. failed.".format(group))
            return ""

        elif arguments["remove"]:
            members = Parameter.expand(arguments["NAMES"])

            group = arguments["--group"] or Default.group

            for member in members:
                result = Group.remove(group, member)

                if result:
                    Console.ok(result)
                else:
                    Console.error(
                        "remove {} from group {}. failed.".format(group, member))
            return ""

        elif arguments["copy"]:
            _from = arguments["FROM"]
            _to = arguments["TO"]

            Group.copy(_from, _to)
            return ""

        elif arguments["merge"]:
            _groupA = arguments["GROUPA"]
            _groupB = arguments["GROUPB"]
            _mergedGroup = arguments["MERGEDGROUP"]

            Group.merge(_groupA, _groupB, _mergedGroup)
            return ""
        
        """
