# Cloudmesh Database (ok)

Cloudmesh stores its status in a database so that you can easily remember which
services you used where and have an accurate account of them. We use as a
database mongoDB to store this information. To use cloudmesh you simply need to
create and start the database service.

First, you need to create a MongoDB database with

```bash
$ cms admin mongo create
```
Second, you need to start it with below command (for windows platform, open a new command prompt)

```bash
$ cms admin mongo start
```

Now you can interact with it to find out the status, the stats, and the database
listing with the commands

```bash
$ cms admin mongo status
$ cms admin mongo stats
$ cms admin mongo list
```

To stop it from running use the command

```bash
$ cms admin mongo stop
```

The database will be started on the information as specified in
`~/.cloudmesh/cloudmesh4.yaml`

An example is


```
    mongo:
      MONGO_AUTOINSTALL: True
      MONGO_BREWINSTALL: False
      LOCAL: ~/local
      MONGO_HOME: ~/local/mongo
      MONGO_PATH: ~/.cloudmesh/mongodb
      MONGO_LOG: ~/.cloudmesh/mongodb/log
      MONGO_DBNAME: 'cloudmesh'
      MONGO_HOST: '127.0.0.1'
      MONGO_PORT: '27017'
      MONGO_USERNAME: 'admin'
      MONGO_PASSWORD: TBD
      MONGO_DOWNLOAD:
        darwin: https://fastdl.mongodb.org/osx/mongodb-osx-ssl-x86_64-4.0.4.tgz
        linux: https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-4.0.4.tgz
        win32: https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-4.0.4-signed.msi
        redhat: https://repo.mongodb.org/yum/redhat/7/mongodb-org/4.0/x86_64/RPMS/mongodb-org-server-4.0.4-1.el7.x86_64.rpm
```

We also provide a convenient install script that downloads the version defined
in the yaml file and installs it in the system with the command. In case of windows platform, 
you will have to set the PATH variable manually after install

```bash
$ cms admin mongo install
```

