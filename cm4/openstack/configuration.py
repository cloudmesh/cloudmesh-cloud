#!/usr/bin/env python3


'''
Configuration manager
Help load running parameters from yaml file
'''

import yaml
import sys





class configuration(object):

    def __init__(self, debug=False):
        '''
        :param debug: enables debug information to be printed
        '''

        self.yaml = "/Users/ruili/Dropbox/FA18-E516/cm/cm4"
        self.debug = debug

