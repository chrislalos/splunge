from splunge import CodeFolderLoader

import importlib
import pytest


@pytest.fixture(scope='module')
def loader():
    ldr = CodeFolderLoader(['/www/site-03', '/www/site-03/code', '/www/site-03/content'])
    ldr.install()
    yield ldr
    ldr.uninstall()


def test_import(loader):
    mod = importlib.import_module('codefolder.hello')
    assert mod is not None
    check_mod_vals(mod)


def test_first_match_wins(loader):
    mod = importlib.import_module('codefolder.rel2')
    assert mod.name == 'MEAAAAATTTTT!!!!!'


def test_template_folder_not_in_code_folders(loader):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module('codefolder.rel4')


def check_mod_vals(mod):
    assert mod.name == 'meat'
    assert mod.relName == 'MEAT'
    assert mod.rel2Name == 'MEAAAAATTTTT!!!!!'
    assert mod.rel3Name == '3 Meat'
    assert mod.rel4Name == '(neat!)'
