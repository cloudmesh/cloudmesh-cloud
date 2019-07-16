# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 2018

@author: Rui
"""

import pprint as pp

from deprecated.draft.openstack import OpenstackCM, OpenstackRefactor


# testcode
# need extra waiting time so server can finish update the node states
def main():
    d = OpenstackCM('chameleon')
    r = OpenstackRefactor(d)
    sizes = r.list_sizes()
    images = r.list_images()
    with open("images.txt", "w") as f:
        for im in images:
            pp.pprint(im.__dict__, f)
    with open("sizes.txt", "w") as f:
        for s in sizes:
            pp.pprint(s.__dict__, f)


if __name__ == "__main__":
    main()
