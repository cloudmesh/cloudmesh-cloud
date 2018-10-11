#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cm controler.

Usage:
  awscm.py resource add <yaml_file>
  awscm.py resource list [--debug]
  awscm.py resource remove <label_name>
  awscm.py resource view <label_name>
  awscm.py copy instance <label_name> file <file> to <where> 
  awscm.py copy instance <label_name> foler <foler> to <where> 
  awscm.py list instance <label_name> from <where>
  awscm.py delete instance <label_name> file <file> from <where> 
  awscm.py delete instance <label_name> folder <folder> from <where>
  awscm.py create instance <label_name> folder <folder> in <where>
  awscm.py read instance <label_name> file <file> from <where>
  awscm.py download instance <label_name> file <file> from <where> to <local>
  awscm.py download instance <label_name> folder <folder> from <where> to <local>
  awscm.py check instance <label_name> process_name <process>
  awscm.py run instance <label_name> local <scripts>
  awscm.py run instance <label_name> remote <scripts>
  awscm.py run local <scripts>
  awscm.py run remote <scripts>
  awscm.py run advanced <string>


  
Options:
  -h --help     Show this screen.

Description:
   this is a basic python code to access remote instance, and this program
   could be used to execute the scripts in remote instances.
   
"""
"""
Inplementation notes

Version 0.1:

* basic docopts version with elementary functionality
* basic classes

"""

from docopt import docopt
import yaml
from resource import Resource
from config import Config
from utility import Utility
from run import Run
from advanced import Advanced
  
    
def process_arguments(arg):
    """
    Processes all the input arguments and acts relative processes.

    :param arg: input arguments for the awscm.
    """
    debug = arg.get('--debug')
    resource = Resource(debug=debug)
    config = Config(debug=debug)
    run = Run(debug=debug)
    advanced = Advanced(debug=debug)
    
    config.config()
    utility = Utility(debug=debug)
    regular_file = config.get_config()

    if arg.get('add') & arg.get('resource'):
        resource.add(regular_file, arg.get('<yaml_file>'))
    
    if arg.get('list') & arg.get('resource'):
        print(yaml.dump(regular_file))
        
    if arg.get('remove') & arg.get('resource'):
        resource.remove(regular_file, arg.get('<label_name>'))
        
    if arg.get('view') & arg.get('resource'):
        print(yaml.dump(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default())))
    
    if arg.get('copy') & arg.get('file'):
        output = utility.copy_file(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<file>'), arg.get('<where>'))
        print(output)
            
    if arg.get('copy') & arg.get('folder'):
        output = utility.copy_folder(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<folder>'), arg.get('<where>'))
        print(output)
            
    if arg.get('list') & arg.get('instance'):
        output = utility.dir_list(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()),arg.get('<file>'), arg.get('<where>'))
        print(output)
        
    if arg.get('delete') & arg.get('file'):
        output = utility.delete_file(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<file>'), arg.get('<where>'))
        print(output)
        
    if arg.get('delete') & arg.get('folder'):
        output = utility.delete_folder(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<folder>'), arg.get('<where>'))
        print(output)
    
    if arg.get('create') & arg.get('folder'):
        output = utility.create_folder(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<folder>'), arg.get('<where>'))
        print(output)
        
    if arg.get('read') & arg.get('file'):
        output = utility.read_file(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<file>'), arg.get('<where>'))
        print(output)
        
    if arg.get('download') & arg.get('file'):
        output = utility.download_file(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<file>'), arg.get('<where>'), arg.get('<local>'))
        print(output)
        
    if arg.get('download') & arg.get('folder'):
        output = utility.download_folder(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<folder>'), arg.get('<where>'), arg.get('<local>'))
        print(output)
        
    if arg.get('check') & arg.get('process_name'):
        output = utility.check_process(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<process>'))
        print(output)
    
    if arg.get('run') & arg.get('instance') & arg.get('local'):
        output = run.run_instance_local(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<scripts>'))
        for i in output:
            print(i)
        
    elif arg.get('run') & arg.get('local'):
        output = run.run_local_or_remote(arg.get('<scripts>'), True)
        for i in output:
            print(i)
        
    if arg.get('run') & arg.get('instance') & arg.get('remote'):
        output = run.run_instance_remote(resource.review(arg.get('<label_name>'), config.get_cloud(), config.get_cluster(), config.get_default()), arg.get('<scripts>'))
        for i in output:
            print(i)
        
    elif arg.get('run') & arg.get('remote'):
        output = run.run_local_or_remote(arg.get('<scripts>'), False)
        for i in output:
            print(i)   
    
    if arg.get('run') & arg.get('advanced'):
        advanced.formula(arg.get('<string>'))
    
    
    
def main():
    """
    Main function for the awscm controler. Processes the input arguments.
    """
    arguments = docopt(__doc__, version='Cloudmesh Vagrant Manager 0.1')
    process_arguments(arguments)
    
if __name__ == "__main__":
    main()
