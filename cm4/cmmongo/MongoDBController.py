import os, subprocess, yaml, time
from sys import platform
from pymongo import MongoClient
from cm4.configuration.config import Config
from pprint import pprint


class MongoDBController(object):
    #version 0.1: for AWS Ubuntu only
    #ubuntu: 18.04
    #if you use other verions, please update the information.
    
    def __init__(self):

        self.config = Config()
        self.host = self.config.get('data.mongo.MONGO_HOST')
        self.username = self.config.get('data.mongo.MONGO_USERNAME')
        self.password = self.config.get('data.mongo.MONGO_PASSWORD')
        self.port = int(self.config.get('data.mongo.MONGO_PORT'))

        self.mongo_path = os.path.join (os.path.dirname (os.path.realpath (__file__)), "MongoDB")
        self.mongo_download = self.config.get('data.mongo.MONGO_DOWNLOAD')
        self.mongo_db_path = self.config.get('data.mongo.MONGO_FOLDER')

    
        
    def check_mongo_dir_and_install(self):
        if not os.path.isdir(os.path.join(os.path.dirname(__file__), "MongoDB")):
            print("MongoDB is not installed in " + os.path.join(os.path.dirname(__file__), "MongoDB"))
            print("Auto-install the MongoDB into "+ os.path.join(os.path.dirname(__file__), "MongoDB"))
            
            if platform == 'linux':
                self.install_mongo_linux()
            if platform == 'darwin':
                self.install_mongo_darwin()
            if platform == 'windows':
                # TODO
                print('next update')
            
    def install_mongo_linux(self):
        #create MongoDB folder in current path
        cmd = 'mkdir %s' % self.mongo_path
        subprocess.check_output(cmd, shell=True)
        #install prepartion tools
        cmd = 'sudo apt-get --yes install libcurl4 openssl'
        subprocess.check_output(cmd, shell=True)
        #download the last version of MongoDB
        cmd = 'wget -P %s %s' % (self.mongo_path, self.mongo_download)
        subprocess.check_output(cmd, shell=True)
        #extract content
        cmd = 'tar -zxvf "%s" -C %s' % (os.path.join(self.mongo_path, self.download_file), self.mongo_path)
        subprocess.check_output(cmd, shell=True)
        #update the mongodb folder path into yaml
        cmd = 'ls %s' % self.mongo_path
        output = str (subprocess.check_output (cmd, shell=True).decode ("utf-8")).split ('\n')

        for i in output:
            print (i)
            if i is not self.download_file and i is not '':
                self.mongo_db_path = os.path.join (self.mongo_path, i)
                self.config.set ('data.mongo.MONGO_FOLDER', self.mongo_db_path)
        #update PATH
        cmd = 'echo "export PATH=%s/bin:$PATH" >> ~/.bashrc ' % self.mongo_db_path
        subprocess.check_output(cmd, shell=True)
        cmd = '. ~/.bashrc'
        subprocess.check_output(cmd, shell=True)
        #create database and log folder
        cmd = 'mkdir %s' % os.path.join(self.mongo_db_path, 'database')
        subprocess.check_output(cmd, shell=True)
        cmd = 'mkdir %s' % os.path.join(self.mongo_db_path, 'log')
        subprocess.check_output(cmd, shell=True)

        #initial mongodb config file
        self.initial_mongo_config(None, None)


    def install_mongo_darwin(self):
        #create MongoDB folder in current path
        cmd = 'mkdir %s' % self.mongo_path
        subprocess.check_output(cmd, shell=True)
        #download the last version of MongoDB
        cmd = 'cd %s;curl -O %s' % (self.mongo_path, self.mongo_download)
        subprocess.check_output(cmd, shell=True)
        #extract content
        cmd = 'tar -zxvf %s -C %s' % (os.path.join(self.mongo_path, self.download_file), self.mongo_path)
        subprocess.check_output(cmd, shell=True)

        # update the mongodb folder path into yaml
        cmd = 'ls %s' % self.mongo_path
        output = str(subprocess.check_output (cmd, shell=True).decode ("utf-8")).split('\n')

        for i in output:
            if i is not self.download_file and i is not '':
                self.mongo_db_path = os.path.join(self.mongo_path, i)
                self.config.set('data.mongo.MONGO_FOLDER', self.mongo_db_path)

        #update PATH
        cmd = 'echo "export PATH=%s/bin:$PATH" >> ~/.bash_profile' % self.mongo_db_path
        subprocess.check_output(cmd, shell=True)
        cmd = '. ~/.bash_profile'
        subprocess.check_output(cmd, shell=True)
        #create database and log folder
        cmd = 'mkdir %s' % os.path.join(self.mongo_db_path, 'database')
        subprocess.check_output(cmd, shell=True)
        cmd = 'mkdir %s' % os.path.join(self.mongo_db_path, 'log')
        subprocess.check_output(cmd, shell=True)

        #initial mongodb config file
        self.initial_mongo_config(False)


    def update_Auth(self):

        # run mongodb
        self.run_mongoDB ()

        # set up auth information
        self.set_auth()

        # shut down mongodb
        self.shutdown_mongoDB ()

        # enable secutiry
        self.initial_mongo_config(True)
        print ("Enable the Secutiry. You will use your username and password to login the MongoDB")
        
        
    def initial_mongo_config(self, security=False):
        default_config_file = dict(net = dict( bindIp = self.host,
                                              port = self.port),
                       storage = dict(dbPath = os.path.join(self.mongo_db_path, 'database'),
                                      journal = dict(enabled = True)),
                       systemLog = dict( destination = 'file',
                                      path = os.path.join(self.mongo_db_path, 'log', 'mongod.log'),
                                      logAppend = True)
                    )
        
        if security:
                default_config_file.update(dict(security = dict(authorization = 'enabled')))
        
        
        with open(os.path.join(self.mongo_db_path,'mongod.conf'), "w") as output:
            try:
                yaml.dump(default_config_file,output, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)  
                
                
    def run_mongoDB(self):
        cmd = 'mongod --dbpath %s --config %s' % (os.path.join(self.mongo_db_path, 'database'), os.path.join(self.mongo_db_path, 'mongod.conf'))
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        print('MonogDB is running')
        
    def shutdown_mongoDB(self):
        '''
        cmd = 'mongod --dbpath %s --shutdown' % os.path.join(self.mongo_db_path, 'database')
        print(cmd)
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        print('MonogDB is stopped')
        '''
        cmd = 'pgrep mongo'
        pid = int(str(subprocess.check_output (cmd, shell=True).decode ("utf-8")).split('\n')[0])
        cmd = 'kill %s' % pid
        subprocess.check_output (cmd, shell=True)
        print('MonogDB is stopped')
        
        
 
    def set_auth(self):
        client = MongoClient(self.host, self.port)
        client.admin.add_user(self.username, self.password, roles = [ { 'role' : "userAdminAnyDatabase", 'db' : "admin" }, "readWriteAnyDatabase" ])
        client.close()


    def dump(self):
        print('dumo')

    def status(self):
        client = MongoClient (self.host, self.port)
        pprint(client.server_info())

        
        

def main():
    test = MongoDBController()
    #test.set_auth()
    #test.check_mongo_dir_and_install()
    #test.install_mongo_darwin()
    #test.update_Auth()
    #test.run_mongoDB()
    #test.shutdown_mongoDB()
    test.status()
    
if __name__ == "__main__":
    main()
