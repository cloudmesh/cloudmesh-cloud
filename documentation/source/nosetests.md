# Nosetests

We use nosetests and not `__main__` to test all functionality so they can me
automatically run and reports can be generated. A project that does not have a
sufficient number of tests to make sure the module works can not be accepted.

To use them you need to install nose with

```bash
$ pip install nose
```

All nose tests are included in the folder `tests`.

* <https://github.com/cloudmesh-community/cm/tree/master/tests>


A simple example is 

* <https://github.com/cloudmesh-community/cm/blob/master/tests/test_key.py>

Note that all tests have specific function names 
of the form

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

Invocation is simply done with the comment lines you see on top that you will include.

in our case the test is called `test_key.py` so we include on the top

```python
#############################################
# nosetest -v --nopature
# nosetests -v --nocapture tests/test_key.py
#############################################
```

you can than execute the test with either command. More information is printed with the command

```bash
$ nosetests -v --nocapture tests/test_key.py
```