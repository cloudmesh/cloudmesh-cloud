# Nosetests

Nosetest is a utility to unit test python code. 

We use nosetests and not `__main__` to test all functionality so they can me
automatically run and reports can be generated. A project that does not have a
sufficient number of tests to make sure the module works can not be accepted.

## Installation

The nose module can be installed with the help of pip utility

```python
$ pip install nose
```

This will install the nose module in the current Python distribution as well 
as a nosetest.exe, which means the test can be run using this utility as well as using `–m` switch.

##  Nosetest Testing Aids

These are the testing aids that is useful, including decorators for restricting test execution time and testing for exceptions.

1. nose.tools.ok_(expr, msg = None) − Shorthand for assert.

2. nose.tools.eq_(a, b, msg = None) − Shorthand for ‘assert a == b, “%r != %r” % (a, b)

3. nose.tools.make_decorator(func) − Wraps a test decorator so as to properly replicate metadata of the decorated function, 
   including nose’s additional stuff (namely, setup and teardown).

4. nose.tools.raises(*exceptions) − Test must raise one of expected exceptions to pass.

5. nose.tools.timed(limit) − Test must finish within specified time limit to pass

6. nose.tools.istest(func) − Decorator to mark a function or method as a test

7. nose.tools.nottest(func) − Decorator to mark a function or method as not a test

Example :
 nose.tools._eq_ that takes two values and compares them using the == operator. U
 pon failure, it gives a nice message, something like "expected 5 but was given 4", 
 helping you to indentify and fix the source of the broken test quickly.

## Directory structure in cloudmesh

All nose tests are included in the folder `tests`.

* <https://github.com/cloudmesh-community/cm/tree/master/tests>

```
+cm
  + cloudmesh
  + tests
    - test_01_topic1.py
    - test_02_topic2.py
    - test_03_topic2.py
```
Note that all tests have specific function names of the form

`def test_number_topic (self)`

the number is defined to order them and is typically something like `001`, note
the leading spaces. the topic is a descriptive term on what we test.

in `def setup(self)` we declare a setup that is run prior to each test being
executed.

an assert simply returns tru or false through a condition that is checked to see 
if the test succeds or fails.

Note that all nosetest functions start with a `HEADING()` which conveniently
prints a banner with the function name and thus helps in debugging in case of
errors.

A simple example is 

* <https://github.com/cloudmesh-community/cm/blob/master/tests/test_key.py>


## Test Case execution 

Nose collects tests from unittest.TestCase subclasses, of course. We can also 
write simple test functions, as well as test classes that are not subclasses of 
unittest.TestCase. nose also supplies a number of helpful functions for writing
timed tests, testing for exceptions, and other common use cases.

Example
:Let us consider nosetest.py

```python
# content of nosetest.py
      def func(x):
         return x + 1
         def test_answer():
         assert func(3) == 5
```
In order to run the above test, use the following command line syntax −

```python
    C:\python>nosetests –v nosetest.py
```

The output displayed on console will be as follows −

```python
      nosetest.test_answer ... FAIL
      ================================================================
      FAIL: nosetest.test_answer
      ----------------------------------------------------------------------
      Traceback (most recent call last):
         File "C:\Python34\lib\site-packages\nose\case.py", line 198, in runTest
            self.test(*self.arg)
         File "C:\Python34\nosetest.py", line 6, in test_answer
            assert func(3) == 5
      AssertionError
      ----------------------------------------------------------------------
      Ran 1 test in 0.000s
      FAILED (failures = 1)
      result = nose.run()
```

The result will be true if the test run is successful, or false if it fails or raises an uncaught exception.
nose supports fixtures (setup and teardown methods) at the package, module, class, and test level. 
As with py.test or unittest fixtures, setup always runs before any test (or collection of tests for 
test packages and modules); teardown runs if setup has completed successfully, regardless of the 
status of the test run.

## Cloudmesh sample test example

```python
#################################################################
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_data_s3.py
#################################################################
from pprint import pprint
import time
import subprocess
import sys
from cloudmesh.common.util import HEADING
from cloudmesh.storage.provider.aws.Provider import Provider
from cloudmesh.management.configuration.config import Config
from cloudmesh.common.Printer import Printer
from cloudmesh.common.FlatDict import FlatDict, flatten
from cloudmesh.management.configuration.SSHkey import SSHkey
from cloudmesh.management.configuration.name import Name
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.util import banner


# ~/.cloudmesh/tmp/storage .....


class TestName:

    def setup(self):
        banner("setup", c="-")
        self.user = Config()["cloudmesh.profile.user"]
        self.p = Provider(name="aws")
        
During development phase you want to use `nosetests -v --nocapture tests/test_key.py`
which prints all print statements also