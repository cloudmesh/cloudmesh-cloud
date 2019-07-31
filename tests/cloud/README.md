# Cloud Tests

IN this directory, you find a number of cloud tests that require you to set 
the cloud prior to the test with

    cms set cloud=CLOUDNAME
    
where cloudname is specified in your `~/.cloudmesh/cloudmesh.yaml` file.
Typical values are:

* chameleon
* aws # To be compleded
* azure # To be completed
* gpogle # To be completed
* docker # To be completed
* virtualbox # To be completed

Important is that you edit the yaml file and add your credentials as described 
in the manual.

List of tests and their status:

* `test_secgroup_provider.py`, test the secgroup in a cloud Provider. 
  However this test does not yet have any assertions and it needs to start from 
  `cms init`, which needs to be added at the top of the test.
  
* `test_sec_command.py`, tests the execution of the sec command. Status unkown

* `test_compute_database.py`, tests the database integration, stutus unkown.

* `test_database.py`, status unkown

* `test_cm_names_find.py`, status unkown

* `test_cm_vm_provider.py`, test an individual cloud vm provider, status not completed

