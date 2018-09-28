#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 17:19:52 2018

@author: yuluo
"""

# TODO: please change to using docopts and integrate in cm4.command.py

import argparse
from cm4.command.resource import Resource
from cm4.command.parallel import ParallelProcess


def main():
    parse = argparse.ArgumentParser(description="Sample help section")
    parse.add_argument("-resource", action="store_true", default=False, dest="res", help="input default resource")
    parse.add_argument("-add", action="store", dest="add_res", help="add resrouce into yaml")
    parse.add_argument("-list", action="store_true", default=False, dest="list_all", help="List all resources")
    parse.add_argument("-remove", action="store", dest="rm_res", help="remove resource from yaml")
    parse.add_argument("--run", action="store_true", default=False, dest="conn", help="connect to computer")
    parse.add_argument("-run", action="append", nargs=2, metavar=("NAME/LABEL", "Script"), dest="run",
                       help="run in labeled/named computer")
    parse.add_argument("--label", action="append", nargs=2, metavar=("Label", "Script"), dest="label",
                       help="run in labeled computer")
    parse.add_argument("--name", action="append", nargs=2, metavar=("Name", "Script"), dest="name",
                       help="run in named computer")
    result = parse.parse_args()

    resource = Resource()
    content = resource.readFile("/Users/yuluo/Desktop/cloudmesh.yaml")
    run = ParallelProcess(content)

    if result.res:
        if result.add_res:
            resource.add(content, str(result.add_res))
        if result.list_all:
            resource.listAll(content)
        if result.rm_res:
            resource.remove(content, str(result.rm_res))

    elif result.run:

        scripts = (result.run[0])[1]
        output = run.run_parall(scripts)
        run.readable(output)
        # item, username, publickey = run.get_computer("one")
        # print(run.run_remote(username, publickey, "/home/ubuntu/cm.sh"))
        # run.run_local(username, publickey, "/Users/yuluo/Desktop/cm.sh")
        # run.delete(username, publickey, "/home/ubuntu/cm.sh")

    elif result.conn:
        if result.label:
            item, username, publickey = run.get_computer((result.label[0])[0])
            output = run.run_remote(username, publickey, (result.label[0])[1])
            run.readable(output)
        if result.name:
            item, username, publickey = run.get_computer((result.name[0])[0])
            output = run.run_local(username, publickey, (result.name[0])[1])
            run.readable(output)
    else:
        print("Syntax error: please use python command-run-draft.py -h")


if __name__ == "__main__":
    main()
