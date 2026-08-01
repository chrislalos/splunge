from splunge import CodeFolderLoader

import importlib
import pytest


@pytest.fixture(scope='module')
def loader():
    ldr = CodeFolderLoader(['/www/site-01'])
    ldr.install()
    yield ldr
    ldr.uninstall()


def test_import(loader):
    mod = importlib.import_module('codefolder.hello')
    assert mod is not None
    check_mod_vals(mod)


def test_first_match_wins(loader):
    mod = importlib.import_module('codefolder.hello')
    assert 'site-01' in mod.__spec__.origin


def check_mod_vals(mod):
    assert mod.name is not None
    assert mod.name == 'meat'
    assert mod.relName is not None
    assert mod.relName == 'MEAT'
