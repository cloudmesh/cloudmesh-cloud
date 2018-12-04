# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 00:12:19 2018

@author: Rui
"""

from cm4.vm.Vm import Vm
from cm4.vm.VmRefactor import VmRefactor
from time import sleep
import datetime
from pprint import pprint


def openstack_test1():
    """
    1. test for openstack
    """
    vm = Vm('chameleon')
    refactor = VmRefactor(vm)

    names = vm.list()  # instances
    sizes = refactor.list_sizes()  # available sizes
    images = refactor.list_images()  # available images

    ## create new instance if necessary
    ## create and auto start
    print("creating instance with provider: chameleon")
    node = vm.provider.create('testgroup-experiment-01')
    node_id = node.id
    name = node.name
    while vm.info(name).state == 'pending':
        sleep(3)
    print("At time " + str(datetime.datetime.now()) + " the state is " + vm.info(name).state)
    print(node)
    print("Node:" + node_id + " has been set up")

    # name = vm.list()[0].name
    # print("We are testing with cloud provider: chameleon, node name: %s " % name)
    # print("At time " + str(datetime.datetime.now()) + " the state is " + str(vm.info(name).state))

    # resize test - checked
    # *** chameleon requires extra confirmation for resizing request
    input("Press Enter to continue...")
    print("resizing.........")
    sizes = refactor.list_sizes()
    print(sizes)
    refactor.resize(name=name, size=sizes[2])  # resize to medium
    print("resizing finished")

    input("Press Enter to continue...")
    node = refactor.confirm_resize(name)
    print("resizing confirmed")

    # change image test - checked
    input("Press Enter to continue...")
    print("refactoring image.............")
    print(images)
    node = refactor.rebuild(name, image=images[2])
    print("image changed")

    # rename test - checked
    input("Press Enter to continue...")
    node = refactor.rename(name, "new name")

    ## destroy
    input("Press Enter to continue...")
    print("call d.destroy() function")
    vm.destroy(name)
    sleep(10)


def aws_test():
    """
    2. test for aws
    """
    pass


def azure_test():
    """
    3. test for azure
    """
    pass


def main():
    input("Press Enter to continue testing for Chameleon cloud....")
    openstack_test1()
    return

    # TODO: need more tests for other provider
    input("Press Enter to continue testing for AWS cloud....")
    aws_test()

    input("Press Enter to continue testing for Azure cloud....")
    azure_test()


if __name__ == "__main__":
    main()
