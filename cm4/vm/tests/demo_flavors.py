# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 00:12:19 2018

@author: Rui
"""


from cm4.vm.Vm import Vm
from cm4.vm.VmRefactor import VmRefactor
from pprint import pprint

def main():

    # test for openstack
    # input("Press Enter to connect to MongoDB....")
    openstack = Vm('chameleon')
    openstack.start('cm_test_small')


    
    print(openstack.mongo.username)
    print(openstack.mongo.password)
    print(openstack.mongo.client)
    print(openstack.mongo.db['config'])
    #print(openstack.mongo.db.collection_names(include_system_collections=False))


    list = openstack.list()
    pprint(list)
    pprint(list[0])

    print(openstack.info('cm_test_small'))


    name = openstack.list()[0].name
    refactor = VmRefactor(openstack)

    sizes = refactor.list_sizes()

    refactor.resize(name=name, size=sizes[1])



    return  # test openstack first


    # TODO: need more tests for other provider


    # test for aws
    input("Press Enter to continue testing for AWS cloud....")
    provider = Vm('aws')
    refactor = VmRefactor(provider)


    # test for azure
    input("Press Enter to continue testing for Azure cloud....")
    provider = Vm('azure')






    provider.mongo.close_client()

if __name__ == "__main__":
    main()