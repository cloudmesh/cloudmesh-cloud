from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import os
from cm4.configuration.config import Config


class OpenstackCM (CloudManagerABC):
   
    def __init__(self, cloud=None):
        config = Config()
        self.cloud = cloud
        if cloud:
            self.os_config = config.get('cloud.{}'.format(cloud))
            self.driver = self._get_driver(cloud)
        else:
            self.os_config = config
            self.driver = None
    
    def _get_obj_list(self,obj_type):
        if obj_type == 'node':
            obj_list = self.driver.list_nodes()
        elif obj_type == 'image':
            obj_list = self.driver.list_images()
        elif obj_type == 'size':
            obj_list = self.driver.list_sizes()
            
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
    
    def _get_driver(self, cloud):
        credential = self.os_config.get("credentials")    
        Openstack = get_driver(Provider.OPENSTACK)
        driver = Openstack(
            credential.get('OS_USERNAME'),
            credential.get('OS_PASSWORD') or os.environ['OS_PASSWORD'], 
            ex_force_auth_url = credential.get("OS_AUTH_URL"),
            ex_force_auth_version='2.0_password',     
            ex_tenant_name = credential.get("OS_TENANT_NAME"),
            ex_force_service_region = credential.get("OS_REGION_NAME")           
            )
        return driver

    def get_driver(self, cloud=None):
        if not cloud and not self.driver:
            raise ValueError('driver not exist: call get_driver() with "cloud" arguement')
        elif not cloud and self.driver:
            return self.driver        
        else:
            self.driver=self._get_driver(cloud)
            return self.driver
        
    def set_cloud(self, cloud):
        self.cloud=cloud
        self.os_config = Config().get('cloud.{}'.format(cloud))
                
    def ls(self):
        """
        list all nodes
        :return: list of id, name, state
        """
        nodes = self.driver.list_nodes()
        return [dict(id=i.id, name=i.name, state=i.state) for i in nodes]

    def info(self, node_id):
        """
        get clear information about one node
        :param node_id:
        :return: metadata of node
        """
        nodes = self.driver.list_nodes()
        for i in nodes:
            if i.id == node_id:
                return dict(id=i.id, name=i.name, state=i.state, public_ips=i.public_ips, private_ips=i.private_ips,
                            size=i.size, image=i.image, created_date=i.created_at.strftime ("%Y-%m-%d %H:%M:%S"), extra=i.extra)


    def create(self, name, image=None, size=None, **kwargs):
        # get defualt if needed
        image_name = image if image else self.os_config.get('default').get('image')
        size_name = size if size else self.os_config.get('default').get('flavor')

        # add to kwargs
        kwargs['name'] = name
        kwargs['image'] = self._get_obj_by_name('image', image_name)
        kwargs['size'] = self._get_obj_by_name('size', size_name)                      
        return self.driver.create_node(**kwargs)

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

    def destroy(self, node_id):
        """
        delete the node
        :param node_id:
        :return: True/False
        """
        node = self._get_node_by_id(node_id)
        return self.driver.destroy_node(node)       

#%% testcode
#d= OpenstackCM('chameleon')
#ndoe = d.create('cm_test')
#node_id = node.id
#d.ls()
#d.info(node_id)
#d.start(node_id)
#d.destroy(node_id)
#d.info(node_id)
#d.ls()


