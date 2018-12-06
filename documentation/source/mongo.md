# Cloudmesh Database

Cloudmesh stores its status in a database so that you can easily remember which services you used where and have an accurate account of them.

We use as a database mongoDB to store this information

To use cloudmesh you simply need to start the database service.

Note: In futire versions this is done automatically. For nw we just od it by hand


You can start the database service with

```bash
$ cm4 admin mongo start
```

You can stop the database service with

```bash
$ cm4 admin mongo start
```

You can test the database service with

```bash
$ cm4 admin mongo status
```

The database will be started on teh port as specified in `~/.cloudmesh/cloudmesh4.yaml`

Additional values can be specivied or are available to locate the downloads.

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
        windows: https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-4.0.4-signed.msi
        redhat: https://repo.mongodb.org/yum/redhat/7/mongodb-org/4.0/x86_64/RPMS/mongodb-org-server-4.0.4-1.el7.x86_64.rpm
```

TODO: describe the parameters
