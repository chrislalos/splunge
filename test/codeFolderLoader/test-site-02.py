from splunge import CodeFolderLoader

import importlib
import os.path
import pytest


paths = ['/www/site-02', '/www/site-02/code']

@pytest.fixture(scope='module')
def loader():
    ldr = CodeFolderLoader(paths)
    ldr.install()
    yield ldr
    ldr.uninstall()


def test_import(loader):
    mod = importlib.import_module('codefolder.hello')
    assert mod is not None
    check_mod_vals(mod)


def test_first_match_wins(loader):
    mod = importlib.import_module('codefolder.rel2')
    print(f'mod.__spec__.origin={mod.__spec__.origin}')
    assert paths[0] == os.path.dirname(mod.__spec__.origin)


def check_mod_vals(mod):
    assert mod.name is not None
    assert mod.name == 'meat'
    assert mod.relName is not None
    assert mod.relName == 'MEAT'
    assert mod.rel2Name is not None
    assert mod.rel2Name == 'MEAAAAATTTTT!!!!!'
