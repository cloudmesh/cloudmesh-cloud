# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 2018

@author: Rui
"""

from deprecated.draft.openstack import OpenstackCM, OpenstackRefactor
from time import sleep
import datetime


# testcode
# need extra waiting time so server can finish update the node states
# pending - running - stopped


def main():
    d = OpenstackCM('chameleon')
    r = OpenstackRefactor(d)

    '''
    sizes = r.list_sizes()
    images = r.list_images()
    for im in images:
        pp.pprint(im.__dict__)
    return
    '''

    # create and auto start
    print("call d.create() function")
    node = d.create('cm_test_small')
    node_id = node.id

    print(node)
    print("Node:" + node_id + " has been set up")

    while d.info(node_id)['state'] == 'pending':
        sleep(3)
    print("At time " + str(datetime.datetime.now()) + " the state is " + d.info(node_id)['state'])

    # resize test - checked
    # *** chameleon requires extra confirmation for resizing request
    input("Press Enter to continue...")
    print("resizing.........")
    sizes = r.list_sizes()
    print(sizes)
    r.resize(node_id, sizes[2])  # resize to medium
    print("resizing finished")

    input("Press Enter to continue...")
    node = r.confirm_resize(node_id)
    print("resizing confirmed")

    # change image test - checked
    input("Press Enter to continue...")
    print("refactoring image.............")
    images = r.list_images()
    print(images)
    node = r.rebuild(node_id, image=images[2])
    print("image changed")

    # rename test - checked
    input("Press Enter to continue...")
    node = r.rename(node_id, "new name")

    # destroy
    input("Press Enter to continue...")
    print("call d.destroy() function")
    d.destroy(node_id)
    sleep(10)

    d.ls()


if __name__ == "__main__":
    main()
