Cloud Tests
===========

IN this directory, you find a number of cloud tests that require you to
set the cloud prior to the test with

::

   cms set cloud=CLOUDNAME

where cloudname is specified in your ``~/.cloudmesh/cloudmesh.yaml``
file. Typical values are:

-  chameleon
-  azure
-  aws # To be compleded
-  gpogle # To be completed
-  docker # To be completed
-  virtualbox # To be completed

Important is that you edit the yaml file and add your credentials as
described in the manual.

List of tests and their status:

-  ``test_secgroup_provider.py``, test the secgroup in a cloud Provider.
   However this test does not yet have any assertions and it needs to
   start from ``cms init``, which needs to be added at the top of the
   test.

-  ``test_sec_command.py``, tests the execution of the sec command.
   Status unkown

-  ``test_compute_database.py``, tests the database integration, stutus
   unkown.

-  ``test_database.py``, status unkown

-  ``test_cm_names_find.py``, status unkown

-  ``test_cm_vm_provider.py``, test an individual cloud vm provider,
   status not completed

TODO:

-  tere are a number of specific tests t=still in this directory. These
   teste need to be merged into the general tests so there is no
   duplication. After the functionality is in another test, the test
   from that provider can be deleted. THis way we know which tests are
   not covered.

Running the Tests
-----------------

The tests can be run all at once from this directory with the following commands: 

.. code:: bash

    cms set cloud=CLOUDNAME
    pytest -v --capture=no . 

The test output can be logged for benchmarking. The preferred test format is: 

::

    {year}_{cloud}_{service}_{username}_{cloudmesh-repo}_{testname}.log

Example code for logging:

.. code:: bash

    cms set cloud=CLOUDNAME
    pytest -v --capture=no . > 2020_azure_compute_name_cloudmesh-cloud_tests-cloud.log

Finally, csv data can be extracted for later usage:

.. code:: bash

    cat log_file.log | grep "# csv" > log_file_results.csv


Test Information
----------------

General
~~~~~~~

- Since the suite of tests runs through general cloud provider functionality, 
  if a set of tests is fails or isinterrupted (loss of internet, keyboard interrupt, etc), 
  it is possible temporary resources will be left undestroyed. Most important to note are 
  virtual machines, as leaving these running can incur usage costs. Test vm's follow the 
  naming scheme ``test-username-vm-#`` and should be manually deleted if left behind 
  following testing.

- Various cloud providers have limits on starting new vm's based on subscription type and 
  current usage. Since these tests involve creating and interacting with new vm's, Quota 
  must be available before attempting to use these tests.

Azure
~~~~~

- Ensure that the resource group variable is set to one that exists in Azure. Manual usage 
  of some functionality might succeed in spite of improperly set resource groups, but the 
  tests will not be accurate. Documentation on resource group 
  setup https://cloudmesh.github.io/cloudmesh-manual/accounts/azure.html/ . 

Aws
~~~

- Due to the nature of AWS vm creation, the test can get hung up on the wait command depending 
  on your configuration.

Oracle
~~~~~~

- Hangs on input at the end of testing
