# cm
Cloudmesh v4

Class Assignment: Parallel Remote Jobs
In this assignment, the entire class can participate. We will use a single repo at 

 

* https://github.com/cloudmesh-community/cm 

 

to coordinate the assignment. This assignment can be useful for your projects and reused for your projects to conduct benchmarks on remote machines. The online and residential classes can be used to ask questions and work on this in person. 

 

The goal is to have a configuration file in which we add a number of computers that you can use to execute tasks via ssh calls remotely. We wiill use no fancyful ssh library, but just subprocess. As this task requires possibly more than you can do in a single week, you need to decide which task you like to work on.

 

a) develop a documentation so that the program can be managed via a command line. Use docopts for that. You are not allowed to use other tools

 

b) develop a yaml file in which we manage the remote machines and how you get access to them. This includes how many jobs on the machine can be executed in parallel. 

 

c) develop a task mechanism to manage and distribute the jobs on the machine using subprocess and a queue. Start with one job per machine, 

 

c.1) take c and do a new logic where each machine can take multiple jobs

 

d) develop a mechnism to start n vms via vagrant 

 

e) develop a test program that distributes a job to the machines calculates the job and fetches the result back. This is closely related to c, but instead of integrating it in c the movement of the data to and from the job is part of a separate mechanism, It is essentially the status of the calculation. Once all results are in do the reduction into a single result. Remember you could do result calculations in parallel even if other results are not there i

 

f) advanced: develop a string based formulation of the tasks while providing the task in a def and using the chars | for parallel, ; for sequential and + for adding results

 

For example

 

def a():

   sting to be executed via ssh on a remote machine

 

def b():

   ...

 

(a | b| c); d; a+ b+ c +d

 

this is not yet well defined hence advanced

 

all others we can easily do 


## Manual: Cloudmesh Multi Service Data Access

### Database Providers

A central database provider keeps track of files stored with multiple cloud services.

#### Local

The [`LocalDBProvider`](db/LocalDBProvider.py) uses a folder on the local file system or network share to store each cloud file entry as a yaml file.


#### MongoDB

Todo


### Storage Providers

Storage providers are services that allow storing files.

#### Local

The [`LocalStorageProvider`](storage/LocalStorageProvider.py) uses a folder on the local file system or network share to act as a "cloud" storage provider.

#### Azure Blob Storage

See Libcloud's [Azure Blobs Storage Driver Documentation](https://libcloud.readthedocs.io/en/latest/storage/drivers/azure_blobs.html) for instructions on how to setup a storage account and generate access keys.

### Getting Started

The default [`cmdata.yaml`](cmdata.yaml) is setup to use a local database and storage provider. 

**Download**

```
git clone https://github.com/cloudmesh-community/cm
cd cm
pip install -r requirements.txt
cd data
```

**Add a file to the default storage service**
```
python cmdata.py add test/files/hello.txt
```

If you're using an unmodified `cmdata.yaml` local test directories are set as the default "service".
An entry for the added file will appear in the local db folder [`test/db`](test/db) and the file 
will be stored in [`test/storage`](test/storage). 

*Note: Network shares can also be used with the local storage provider.*

**List all files**
```
python cmdata.py ls
```

**Download file**
```
python cmdata.py get hello.txt ../test
```

**Delete file**
```
python cmdata.py del hello.txt
```

### TODO - DATA

- [ ] The output for `ls` is not well formatted for the length of URLs.
- [ ] Access/sharing policies
- [ ] MongoDB database provider
- [ ] Google Drive integration
- [ ] Box integration
- [ ] AWS integration
- [ ] Command line option for config file path
- [ ] Should settings be moved to `cloudmesh.yaml`?
- [ ] Better way to determine which storage providers to load