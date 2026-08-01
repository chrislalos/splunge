from splunge import CodeFolderLoader

import importlib
import pytest
import sys


@pytest.fixture(scope='module')
def loader():
    sys.path.insert(0, '/www/site-05')
    ldr = CodeFolderLoader(['/www/site-05'])
    ldr.install()
    yield ldr
    ldr.uninstall()
    sys.path.remove('/www/site-05')


def test_import(loader):
    mod = importlib.import_module('codefolder.hello')
    assert mod is not None
    check_mod_vals(mod)


def test_stdlib_import(loader):
    import os as _os
    assert _os is not None


def test_third_party_import(loader):
    import pytest as _pytest
    assert _pytest is not None


def check_mod_vals(mod):
    assert mod.name == 'hello'
    assert mod.fooName == 'FOO'
    assert mod.foo.name == 'FOO'
    assert mod.barName == 'BAR'
    assert mod.bar.name == 'BAR'
    assert mod.bumName == 'BUM'
    assert mod.bum.name == 'BUM'
