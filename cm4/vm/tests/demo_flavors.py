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
    refactor = VmRefactor(openstack)
    #openstack.create('ruili-01')


    #print(openstack.mongo.username)
    #print(openstack.mongo.password)
    #print(openstack.mongo.client)
    #print(openstack.mongo.db)
    #print(openstack.mongo.db.collection_names(include_system_collections=False))


    list = openstack.list()
    #pprint(list)
    #pprint(list[0])

    print(openstack.info('ruili-01'))


    name = openstack.list()[0].name
    print(name)

    sizes = refactor.list_sizes()
    pprint(sizes)

    refactor.resize(name=name, size=sizes[3])



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