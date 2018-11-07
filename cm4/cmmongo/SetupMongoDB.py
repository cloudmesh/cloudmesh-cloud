#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 01:51:00 2018

@author: yuluo
"""
import os, subprocess, yaml, time
from sys import platform
from pymongo import MongoClient


class SetupMongoDB(object):
    #version 0.1: for AWS Ubuntu only
    #ubuntu: 18.04
    #if you use other verions, please update the information.
    
    def __init__(self):
        self.mongo_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "MongoDB")
        self.mongo_download = 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1804-4.0.3.tgz'
        self.mongo_db_path = os.path.join(self.mongo_path, 'mongodb-linux-x86_64-ubuntu1804-4.0.3')
        
        #if the coloudmesh.yaml file mentioned where to install mongodb and other information, then we will set the information by using config.py
        
    
        
    def check_mongo_dir(self):
        if not os.path.isdir(os.path.join(os.path.dirname(__file__), "MongoDB")):
            print("MongoDB is not installed in " + os.path.join(os.path.dirname(__file__), "MongoDB"))
            print("Auto-install the MongoDB into "+ os.path.join(os.path.dirname(__file__), "MongoDB"))
            
            if (platform == 'linux'):
               self.install_mongo_linux()
            
            
            
            
    def install_mongo_linux(self):
        #create MongoDB folder in current path
        cmd = 'mkdir %s' % self.mongo_path
        subprocess.check_output(cmd, shell=True)
        #install prepartion tools
        cmd = 'sudo apt-get --yes install libcurl4 openssl'
        subprocess.check_output(cmd, shell=True)
        #download the last version of MongoDB
        cmd = 'wget -P "%s" %s' % (self.mongo_path, self.mongo_download) 
        subprocess.check_output(cmd, shell=True)
        #extract content
        cmd = 'tar -zxvf "%s" -C %s' % (os.path.join(self.mongo_path, 'mongodb-linux-x86_64-ubuntu1804-4.0.3.tgz'), self.mongo_path)
        subprocess.check_output(cmd, shell=True)
        #update PATH
        cmd = 'echo "export PATH=%s/bin:$PATH" >> ~/.bashrc ' % self.mongo_db_path
        subprocess.check_output(cmd, shell=True)
        #create database and log folder
        cmd = 'mkdir %s' % os.path.join(self.mongo_db_path,'database')
        subprocess.check_output(cmd, shell=True)
        cmd = 'mkdir %s' % os.path.join(self.mongo_db_path,'log')
        subprocess.check_output(cmd, shell=True)
        
        #user input port, username, password
        print("Please remember the port, username, password infromation")
        self.port = int(input("The Port open for MongoDB (default: 27017):"))
        self.username = input("The username used in MongoDB:")
        self.password = input("The password for that username:")
        
        #initial mongodb config file
        self.initial_mongo_config(None, None)
        
        #run mongodb
        self.run_mongoDB()
        
        #set up auth information
        self.set_auth()
        
        #shut down mongodb
        self.shutdown_mongoDB()
        
        #enable secutiry
        self.initial_mongo_config(self.username, self.password)
        print("Enable the Secutiry. You will use your username and password to login the MongoDB")

        time.sleep(2)

        self.run_mongoDB()

        
        
        
    def initial_mongo_config(self, username, password):
        default_config_file = dict(net = dict( bindIp = '0.0.0.0',
                                              port = self.port),
                       storage = dict(dbPath = os.path.join(self.mongo_db_path, 'database'),
                                      journal = dict(enabled = True)),
                       systemLog = dict( destination = 'file',
                                      path = os.path.join(self.mongo_db_path, 'log', 'mongod.log'),
                                      logAppend = True)
                    )
        
        if (username != None and password != None):
                default_config_file.update(dict(security = dict(authorization = 'enabled')))
        
        
        with open(os.path.join(self.mongo_db_path,'mongod.conf'), "w") as output:
            try:
                yaml.dump(default_config_file,output, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)  
                
                
    def run_mongoDB(self):
        #mongod --dbpath /home/ubuntu/MongoDB/mongodb-linux-x86_64-ubuntu1804-4.0.3/db/ --config /home/ubuntu/MongoDB/mongodb-linux-x86_64-ubuntu1804-4.0.3/mongod.conf
        cmd = 'mongod --dbpath %s --config %s' % (os.path.join(self.mongo_db_path, 'database'), os.path.join(self.mongo_db_path, 'mongod.conf'))
        subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        print('MonogDB is running')
        
    def shutdown_mongoDB(self):
        #mongod --dbpath /home/ubuntu/MongoDB/mongodb-linux-x86_64-ubuntu1804-4.0.3/db/ --shutdown
        cmd = 'mongod --dbpath %s --shutdown' % os.path.join(self.mongo_db_path, 'database')
        subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        print('MonogDB is stopped')
        
        
 
    def set_auth(self):
        client = MongoClient('localhost', self.port)
        client.admin.add_user(self.username, self.password, roles = [ { 'role' : "userAdminAnyDatabase", 'db' : "admin" }, "readWriteAnyDatabase" ])
        client.close()
        
        
'''    
def main():
    test = SetupMongoDB()
    test.check_mongo_dir()
    #test.run_mongoDB()
    #test.shutdown_mongoDB()
    
if __name__ == "__main__":
    main()
'''