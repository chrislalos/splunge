import os
import pytest
from splunge import constants, Xgi

_codeFolder = f"/www"



@pytest.fixture(scope='module', autouse=True)
def _setup():
    old = os.getcwd()
    os.chdir(_codeFolder)
    yield
    os.chdir(old)


def test_create_args():
    path = "/www/hello/bar?name=meat"
    xgi = Xgi.create(path)
    # get args
    getArgs = xgi.create_get_args()
    assert getArgs is not None
    assert len(getArgs) == 1
    assert 'name' in getArgs
    assert getArgs['name'] == "meat"
    # post args
    postArgs = xgi.create_post_args()
    assert postArgs is not None
    assert len(postArgs) == 0
    # all args
    args = xgi.create_args()
    assert args is not None
    assert len(args) == 1
    assert 'name' in args
    assert args['name'] == "meat"


def test_get_module_name():
    path = "/hello/foo"
    xgi = Xgi.create(path)
    assert xgi.get_module_name() == f'{constants.NSP_name}.hello.foo'


def test_get_module_path():
    path = '/rel'
    xgi = Xgi.create(path)
    assert xgi is not None
    module_path = xgi.get_module_path(_codeFolder)
    assert os.path.exists(module_path)


def test_is_python_module():
    path = '/foo'
    xgi = Xgi.create(path)
    assert xgi is not None
    assert xgi.is_python_module()


def test_is_python_module2():
    path = '/sub/bum'
    xgi = Xgi.create(path)
    assert xgi is not None
    assert xgi.is_python_module()
