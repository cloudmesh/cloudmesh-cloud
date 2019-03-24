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

## Database Decorator

Cloudmesh comes with a very convenient mechanism to integrate data into MongoDB.
All you have to do is to create a list of dictionaries with a function, that
returns this dictionary and use a decorator in the function to update the
information into the database. 

The data base decorator automatically replaces an entry in the database with
the dictionary returned by a function.

It is added to a MongoDB collection. The location is determined from the
values in the dictionary.

The name of the collection is determined from cloud and kind:

   `cloud-kind`

In addition each entry in the collection has a `name` that must be unique in
that collection.

In most examples it is best to separate the updload from the actual return
class. This way we essentially provide two functions one that provide the
dict and another that is responsible for the upload to the database.

Example:

`cloudmesh.example.foo` contains:

    class Provider(object)

        def entries(self):
            return {
               "cloud": "foo",
               "kind"": "entries",
               "name": "test01"
               "test": "hello"}


`cloudmesh.example.bar` contains:

    class Provider(object)

        def entries(self):
            return {
               "cloud": "bar",
               "kind"": "entries",
               "name": "test01"
               "test": "hello"}

`cloudmesh.example.provider.foo` contains:

    from cloudmesh.example.foo import Provider as FooProvider
    from cloudmesh.example.foo import Provider as BarProvider

    class Provider(object)

        def __init__(self, provider):
           if provider == "foo":
              provider = FooProvider()
           elif provider == "bar":
              provider = BarProvider()

        @DatabaseUpdate
        def entries(self):
            provider.entries()


Separating the database and the dictionary creation allows the developer to
implement different providers but only use one class with the same methods
to interact for all providers with the database.

In the combined provider a find function to for example search for entries
by name across collections could be implemented.
















