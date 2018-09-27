Cloudmesh Multi Service Data Access
===

## Database Providers

A central database provider keeps track of files stored with multiple cloud services.

### Local

The [`LocalDBProvider`](./db/LocalDBProvider.py) uses a folder on the local file system or network share to store each cloud file entry as a yaml file.


### MongoDB

Todo


## Storage Providers

Storage providers are services that allow storing files.

### Local

The [`LocalStorageProvider`](./storage/LocalStorageProvider.py) uses a folder on the local file system or network share to act as a "cloud" storage provider.

### Azure Blob Storage

See Libcloud's [Azure Blobs Storage Driver Documentation](https://libcloud.readthedocs.io/en/latest/storage/drivers/azure_blobs.html) for instructions on how to setup a storage account and generate access keys.

## Getting Started

The default [`cmdata.yaml`](./cmdata.yaml) is setup to use a local database and storage provider. 

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
An entry for the added file will appear in the local db folder [`test/db`](./test/db) and the file 
will be stored in [`test/storage`](./test/storage). 

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

## TODO

- [ ] The output for `ls` is not well formatted for the length of URLs.
- [ ] Access/sharing policies
- [ ] MongoDB database provider
- [ ] Google Drive integration
- [ ] Box integration
- [ ] AWS integration
- [ ] Command line option for config file path
- [ ] Should settings be moved to `cloudmesh.yaml`?
- [ ] Better way to determine which storage providers to load