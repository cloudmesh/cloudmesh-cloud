# -*- coding: utf-8 -*-
"""
Modified on Tue Nov 15 2018

@author: Kimball Wu
@author: Rui
"""

import os
import subprocess
import pprint
from cloudmesh.abstractclass import ComputeNodeManagerABC
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from cloudmesh.management.configuration.config import Config
from time import sleep
from cloudmesh.openstack.OpenstackRefactor import OpenstackRefactor


class OpenstackCM(ComputeNodeManagerABC):

    def __init__(self, cloud=None):
        config = Config().data
        self.cloud = cloud
        self.driver = None
        self.key = None
        if cloud:
            data = config.get('cloudmesh')
            self.os_config = data.get('cloud').get(cloud)
            self.os_config = config.get('cloudmesh').get('cloud').get(cloud)
            self.driver = self.get_driver(cloud)
            self.key = self.os_config.get('credentials').get('OS_KEY_PATH')  # credentials.target return null string
            # if we don't find OS_KEY_PATH in yaml, go to os.environ instead which can be set in .bashrc
            if self.key is None:
                self.key = os.environ['OS_KEY_PATH']
        else:
            self.os_config = config

    def _get_obj_list(self, obj_type):
        obj_list = None
        if obj_type == 'node':
            obj_list = self.driver.list_nodes()
        elif obj_type == 'image':
            obj_list = self.driver.list_images()
        elif obj_type == 'size':
            obj_list = self.driver.list_sizes()
        elif obj_type == 'ip':
            obj_list = self.driver.ex_list_floating_ips()
        return obj_list

    def _get_obj_by_name(self, obj_type, obj_name):
        obj_list = self._get_obj_list(obj_type)
        for o in obj_list:
            if o.name == obj_name:
                return o

    def _get_obj_by_id(self, obj_type, obj_id):
        obj_list = self._get_obj_list(obj_type)
        for o in obj_list:
            if o.id == obj_id:
                return o

    def _get_node_by_id(self, node_id):
        return self._get_obj_by_id('node', node_id)

    def get_driver(self, cloud=None):
        if not cloud:
            raise ValueError('Cloud arguement is not properly configured')
        if not self.driver:
            self.driver = self.get_driver_helper(cloud)
        return self.driver

    def get_driver_helper(self, cloud):
        credential = self.os_config.get("credentials")
        openstack = get_driver(Provider.OPENSTACK)
        driver = openstack(
            credential.get('OS_USERNAME'),
            credential.get('OS_PASSWORD') or os.environ['OS_PASSWORD'],
            ex_force_auth_url=credential.get("OS_AUTH_URL"),
            ex_force_auth_version='2.0_password',
            ex_tenant_name=credential.get("OS_TENANT_NAME"),
            ex_force_service_region=credential.get("OS_REGION_NAME")
        )
        return driver

    def set_cloud(self, cloud):
        """
        switch to another cloud provider
        :param cloud: target provider
        :return:
        """
        self.cloud = cloud
        self.os_config = Config().get('cloud.{}'.format(cloud))

    def _get_public_ip(self):
        ips = [x for x in self._get_obj_list('ip') if not x.node_id]
        # print(self._get_obj_list('ip'))
        # print(ips[0].node_id)
        return ips[0] if ips else None

    # API hack for new VM class

    def ex_start_node(self, node):
        return self.driver.ex_start_node(node)

    def ex_stop_node(self, info, deallocate):
        return self.driver.ex_stop_node(info)

    def destroy_node(self, node):
        return self.driver.destroy_node(node)

    def create_node(self, name):
        return self.create(name)

    def list_nodes(self):
        return self.driver.list_nodes()

    # APIs
    def execute(self, name, command):
        """
        execute arbitrary shell command on node through ssh
        ssh funcionality must available on the local machine
        :param name: name of the VM
        :param command: shell command 
        
        """
        node = self._get_obj_by_name('node', name)
        template = 'ssh -i {key} -o StrictHostKeyChecking=no {user}@{host} "{command}"'
        kwargs = {'key': os.path.splitext(self.key)[0],
                  'user': self.os_config.get('default.username'),
                  'host': node.public_ips[0],
                  'command': command}
        try:
            res = subprocess.check_output(template.format(**kwargs),
                                          shell=True,
                                          input=b'\n',
                                          stderr=subprocess.STDOUT)
            return res.decode('utf8')
        except Exception as e:
            return e

    def set_public_ip(self, name, ip_str):
        """        
        :param name: name of the VM
        :param ip_str: ip string 
        """
        node = self._get_obj_by_name('node', name)
        ip_obj = self.driver.ex_get_floating_ip(ip_str)
        if ip_obj and not ip_obj.node_id:
            self.driver.ex_attach_floating_ip_to_node(node, ip_obj)
        elif ip_obj and ip_obj.node_id:
            raise EnvironmentError('Public IP has been assigned to another machine. Pick another ip')
        else:
            raise ValueError('Public IP addresss does not exist!')

    def remove_public_ip(self, name):
        """        
        :param name: name of the VM
        """
        node = self._get_obj_by_name('node', name)
        for ip in node.public_ips:
            self.driver.ex_detach_floating_ip_from_node(node, ip)

    # standard functions
    def ls(self):
        """
        list all nodes
        :return: list of id, name, state
        """
        nodes = self.driver.list_nodes()
        return [dict(id=i.id, name=i.name, state=i.state) for i in nodes]

    def list_available_ips(self):
        index = 0
        for x in self._get_obj_list('ip'):
            if not x.node_id:
                print("available ip_{}: {}".format(index, x))
                index += 1

    def nodes_info(self):
        """
        get organized meta information about all node
        :return: metadata of node
        """
        nodes = self.driver.list_nodes()
        res = {}
        for i in nodes:
            res[i.id] = dict(id=i.id, name=i.name, state=i.state,
                             public_ips=i.public_ips, private_ips=i.private_ips,
                             size=i.size, image=i.image,
                             created_date=i.created_at.strftime("%Y-%m-%d %H:%M:%S"), extra=i.extra)
        return res

    def info(self, node_id):
        """
        get meta information about one node
        :param node_id:
        :return: metadata of node
        """
        node = self._get_node_by_id(node_id)
        return dict(id=node.id,
                    name=node.name,
                    state=node.state,
                    public_ips=node.public_ips,
                    private_ips=node.private_ips,
                    size=node.size,
                    image=node.image,
                    created_date=node.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    extra=node.extra)

    def list(self):
        return self.driver.list_nodes()

    def create(self, name, image=None, size=None, timeout=300, **kwargs):
        # get defualt if needed
        image_name = image if image else self.os_config.get('default').get('image')
        size_name = size if size else self.os_config.get('default').get('flavor')

        # add to kwargs
        kwargs['name'] = name
        kwargs['image'] = self._get_obj_by_name('image', image_name)
        kwargs['size'] = self._get_obj_by_name('size', size_name)
        if self.key:
            try:
                self.driver.import_key_pair_from_file(name, self.key)
            except Exception as e:
                print(e)
                print("If exception code is 409 Conflict Key pair is already exists, we can still proceed without key importation")
        kwargs['ex_keyname'] = name

        # create node
        node = self.driver.create_node(**kwargs)

        # attach ip if available
        # in case of error, need timeout to make sure we do attachment after the node has been spawned
        ip = self._get_public_ip()
        if ip:
            timeout_counter = 0
            while self.info(node.id)['state'] != 'running':
                if timeout_counter > timeout:
                    print("Node is being spawned for too long, float ip association is failed")
                    return node
                sleep(3)
                timeout_counter += 3
            self.driver.ex_attach_floating_ip_to_node(node, ip)
        return node

    def start(self, node_id):
        """
        start the node
        :param node_id:
        :return: True/False
        """
        node = self._get_node_by_id(node_id)
        return self.driver.ex_start_node(node)

    def stop(self, node_id):
        """
        stop the node
        :param node_id:
        :return:
        """
        node = self._get_node_by_id(node_id)
        return self.driver.ex_stop_node(node)

    def suspend(self, node_id):
        """
        suspend the node
        :param node_id:
        :return: True/False
        """
        node = self._get_node_by_id(node_id)
        return self.driver.ex_suspend_node(node)

    def resume(self, node_id):
        """
        resume the node
        :param node_id:
        :return: True/False
        """
        node = self._get_node_by_id(node_id)
        return self.driver.ex_resume_node(node)

    def reboot(self, node_id):
        """
        resume the node
        :param node_id:
        :return: True/False
        """
        node = self._get_node_by_id(node_id)
        return self.driver.reboot_node(node)

    def destroy(self, node_id):
        """
        delete the node
        :param node_id:
        :return: True/False
        """
        node = self._get_node_by_id(node_id)
        return self.driver.destroy_node(node, )


def process_arguments(arguments):
    """
    Process command line arguments to execute VM actions.
    Called from cm4.command.command
    :param arguments:
    """
    result = None
    node = None
    if arguments.get("--debug"):
        pp = pprint.PrettyPrinter(indent=4)
        print("vm processing arguments")
        pp.pprint(arguments)
    vm = OpenstackCM('chameleon')
    rf = OpenstackRefactor(vm)

    # general info queries
    if arguments.get("list") or arguments.get("ls"):
        result = vm.ls()
    elif arguments.get("sizes"):
        result = rf.list_sizes()
    elif arguments.get("images"):
        result = rf.list_images()
    # common driver operations
    elif arguments.get("create"):
        # TODO: add create method
        pass
    elif arguments.get("start"):
        result = vm.start(node.id)
    elif arguments.get("resume"):
        result = vm.resume(node.id)
    elif arguments.get("stop"):
        result = vm.stop(node.id)
    elif arguments.get("suspend"):
        result = vm.suspend(node.id)
    elif arguments.get("destroy"):
        result = vm.destroy(node.id)
    # refactor operations
    elif arguments.get("resize"):
        target_size = arguments.get("resize")
        result = rf.resize(node.id, target_size)
    elif arguments.get("rename"):
        target_name = arguments.get("rename")
        result = rf.rename(node.id, target_name)
    elif arguments.get("resize"):
        target_image = arguments.get("resize")
        result = rf.rebuild(node.id, target_image)
    # remote cliet connection and authentication operations
    elif arguments.get("ssh"):
        # TODO
        pass

    elif arguments.get("run"):
        # TODO
        pass

    elif arguments.get("script"):
        # TODO
        pass

    return result
