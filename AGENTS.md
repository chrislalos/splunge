#### venv

Running tests and other tasks require a virtual env to be setup and active.
The script scripts/create-venv.env will create a folder named venv. It should be run from the project folder so it can find requirements.txt
The script will do nothing if the venv folder already exists. Do get a fresh venv, you must delete the folder first.
Once the venv is created, source venv/bin/activate will activate the venv, until deactivated with deactivate


#### tools/ folder for tests (or lack thereof)

Other projects have standardized on a tools/ folder for putting test scripts, one-per-task. But Python already has nice standards around where to put tests and how to write them. And while sometimes it's easy to code splunge tests in bash, in general we should keep everything Python that we can. bettywhitelist is a Python web app. Keeping it Python keeps it simple.


#### running tests

tests should be run from the project folder like so: python -m unittest test.[test_module] to run all tests in a class, or test.[test_module].Tests.[test_function] to run a single test
tests generally require an active virtualenv to run successfully. See the venv section for more detail. Without an active venv the tests will be unable to find their dependencies, or splunge code, and since the tests are for splunge, being unable to find splunge is a problem
