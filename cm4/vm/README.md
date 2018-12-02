# VM Description

In cloudmesh cm4 project, we are using the **Python** tool to implement a program that could remotelly controll cloud nodes provided by different organizations and run experiments parallelly in runable machines.

The goal of **cm4** project is to provide a platform that users could directly control the nodes they have, like AWS, Azure, and OPENSTACK instances. Users could decide to start, stop, destory, create, resume, and suspend different nodes without accessing the **Console** interfaces of providers. Then users could install experiment environment, softwares, and other required tools in these running nodes. Finally, an experiment could be executed in running nodes by sending the commands from **cm4** platform. Meanwhile, we embedd the NoSQL database **MongoDB** into project for managing the nodes and experiments.

## Providers *cm4* could access

In this project, we are using the python library [**Apache Libcloud**](https://libcloud.apache.org) to interact with cloud service providers. Currently, in the **cm4** project, we could access:

* [**AWS**](https://aws.amazon.com)
* [**AZURE**](https://azure.microsoft.com/en-us/)
* any cloud service providers using **OPENSTACK**. For example, [**Chameleon**](https://www.chameleoncloud.org) and [**Jetstream**](https://jetstream-cloud.org)

By using the **Apache Libcloud** API, we could do these operations for nodes in above cloud service providers:

* Start the node
* Stop the node
* Resume the node
* Suspend the node
* Destory the node
* Create the node

**Improvement**: Sometimes adjustments to nodes are necessary (switch between different images/OS and service sizes). 
Now our project also allow users to customize their instances across multiple providers by using refactor functions to support their management tasks.
* Resize the node
* Rebuild(with different image) the node
* Rename the node
* Revert previous operations to the node


### AWS

Amazon Web Service (**AWS**) provided by Amazon is a secure cloud service platform, users could start any instances with selected images.

Before users use the **cm4** platform to access **EC2**, they have to finish these preparations:

1. EC2 account, more information is 
   [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)

2. Log in the EC2 account, update your **Access Key**.

   **Access Keys** has two parts: **Access Key ID** 
   and **Secret Access Key**. These **Access Keys** are the only 
   way you    could authentically access the AWS though AWS API requests.
   (create new Access Key: Account 
   (right upper corner) > My Security Credentials > Access Keys > Create New Access Key)

3. **Private Key file** is a key pairs to encrypt and decrypt 
   login information. While using **Private Key file**, there is no 
   need to use username or password to login the instance of AWS. For
   sshing the instance, the ssh client would use the **private key file** 
   instead of credential information. (create new key pairs: Network & Security
   (left column bar) > Key Pairs > Create Key Pair)

4. **Security Group** acts as a virtual firewall for the instance. 
   When you launch a instance, we have to attach the **Security Group** 
   to it for controlling the traffic in and out. So before you are using 
   any nodes in AWS, you have to pre-define the **Security Group** that you will use.
   (create new Security Group: Network $ Security (left column bar) > Security Group > Create Security Group)

5. **Region** is the service location where you start the instance. 
   AWS hosts services in different regions, you should select the region where you want to start you instace.

When you finish all above things, you should update information into the block 'aws' of **chouldmesh4.yaml** file in **ETC** folder

**EC2** provides On-Demand Pricing cloud services based on different CPU, Memory and Storage selections. Please visit this [page](https://aws.amazon.com/ec2/pricing/on-demand/) for more information. In default setting, we use the latest **Ubuntu** image filled in default.image field. If you want to use other images, please update the Image ID into it.


### AZURE

Uses [LibCloud's Azure ARM Compute Driver](https://libcloud.readthedocs.io/en/latest/compute/drivers/azure_arm.html)

### Azure Setup


**Install Azure CLI**

[Download and install according to your platform.](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)

**Make sure subscription is registered for compute services**

```
az provider register --namespace Microsoft.Compute
```

**Service principal**

[Full documentation on creating service principals.](https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest) The Azure ARM Driver does not appear to support certificate based
principals at this time.


Create Principal
```
az ad sp create-for-rbac --name cm-admin-pw --password <SECRET>
```

Add `Owner` role.

```
az role assignment create --assignee <APP_ID> --role Owner
```

*Note:* `<APP_ID>` is provided in the output when the principal is created

### OPENSTACK

OpenStack is an Infrastructure service that allows users to utilize computing resource in cloud service platform through virtual environments. 

[Chameleon Cloud](https://www.chameleoncloud.org/) provides an OpenStack installation of version 2015.1 (Kilo) using the KVM virtualization technology at the KVM@TACC site. It is
important to make sure you are visiting the [KVM@TACC](https://openstack.tacc.chameleoncloud.org/) site so as to get proper installation. Learn more [here](https://chameleoncloud.readthedocs.io/en/latest/technical/kvm.html) 
to properly set up yout account before proceed to your journey with **cm4**.


### Extra: Vargrant

Please refer to [here](https://github.com/cloudmesh-community/cm/tree/master/cm4/vagrant/README.md) to see how to setup Vagrant with cm4.

## [`cloudmesh4.yaml`] configuration file

Sachith


## MongoDB Database

We add the database into **cm4** with two reasons:

* provide the information of nodes in different providers.
* record the experiment executed through cm4, easy for next re-execution.


Everytime the user use the **cm4** platform, the server would access the running MongoDB database, querying the nodes' information, showing relative metadata, and then updating all necessary data.

The **MongoDB** would finish below taskes:

* saving all information:

  1. the nodes' information queryed from cloud service, like name, id, status, and other metadata about this node.
  2. saving the executing or excuted experiment information, like which node we run the experiment, the input, the command, and the output.
  3. saving the group information users defined.
  4. saving the [`cloudmesh4.yaml`] information.

* updating any changes:
  
  1. the changes updated on the nodes, like stop running node, or start stopped node.
  2. the changes updated on the [`cloudmesh4.yaml`], like add new nodes.
  3. when the experiment is done, output and experiment status would be updated.
  4. new group is created while using **cm4** will be updated

* return required information:
	
  1. return the node information, group information, and experiment information when **cm4** queries them.

#### Data Scheme in MongoDB

There are three types of docuemnts in MongoDB:

* Node information in ```cloud``` collection.
  Different cloud service providers would return different schemas of node information. It is hard to manipulate different nodes' information into same schema, so we decide to dump the return mesaage into MongoDB without any changes.
  
* Node's experiment status in ```status``` collection.
  The doucment in ```status``` collection is going to save the information of experiments executed in a node.
  ```
  '_id': node_id,
  'status': status,
  'currentJob': job_id,
  'history': history
  ```
  ```status : node is running a experiment or not```
  ```currentJob : the running experiment id```
  ```history : the history of executed experiments in this node```
  
* Experiment information in ```job``` collection.
  ```
  '_id' : experiment_id
  'name': name,
  'status': status,
  'input': input_info,
  'output': output_info,
  'description': description,
  'commands': commands
  ```
  ```name : the name of the experiment```
  ```status : running or finished```
  ```input : the input data file```
  ```output : the output data file```
  ```description : the description about this experiment```
  ```commands : the commands used in this experiemnt```

* Group information in ```group``` collection. :o2:
  ```
  'cloud': cloud,
  'name': name,
  'size': size,
  'vms': list_vms
  ```
  we are still working on it

#### Security in MongoDB

For data security purpose, we enable the MongoDB security functionality in **cm4** project.

When users first time start the **MongoDB**, they have to add an account and open an port to access all database in MongoDB. Because we save all nodes' information into MongoDB inclduing the *Authorization* information. If your MongoDB is open to everyone, it is easy for hacker to steal your information. So you are requried to set the **username** and **password** for the security purpose. 

If you want to learn more about the **Security** in MongoDB, you can visit this [page](https://docs.mongodb.com/manual/security/) or visit the brief introduction about the MongoDB

Here is a quick reference about how to
 [enable MongoDB Security](https://medium.com/@raj_adroit/mongodb-enable-authentication-enable-access-control-e8a75a26d332) option. Currently our implementation require 
users to access localhost mongoDB client with admin account. 



