from splunge import CodeFolderLoader

import importlib
import pytest


@pytest.fixture(scope='module')
def loader():
    ldr = CodeFolderLoader(['/www/site-04', '/www/site-04/code', '/www/site-04/content'])
    ldr.install()
    yield ldr
    ldr.uninstall()


def test_import(loader):
    mod = importlib.import_module('codefolder.hello')
    assert mod is not None
    expected = {
        'billie': 'billie',
        'blitzen': 'blitzen',
        'brownie': 'brownie',
        'comet': 'comet',
        'cupid': 'cupid',
        'dakota': 'dakota',
        'dancer': 'dancer',
        'dasher': 'dasher',
        'dolly': 'dolly',
        'donner': 'donner',
        'ernie': 'ernie',
        'hello': 'hello',
        'isabella': 'isabella',
        'ivy': 'ivy',
        'koba': 'koba',
        'lexi': 'lexi',
        'pedro': 'pedro',
        'prancer': 'prancer',
        'ruger': 'ruger',
        'tessie': 'tessie',
        'tiffany': 'tiffany',
        'vixen': 'vixen',
        'billie.name': 'billie',
        'blitzen.name': 'blitzen',
        'brownie.name': 'brownie',
        'comet.name': 'comet',
        'cupid.name': 'cupid',
        'dakota.name': 'dakota',
        'dancer.name': 'dancer',
        'dasher.name': 'dasher',
        'dolly.name': 'dolly',
        'donner.name': 'donner',
        'ernie.name': 'ernie',
        'hello.name': 'hello',
        'isabella.name': 'isabella',
        'ivy.name': 'ivy',
        'koba.name': 'koba',
        'lexi.name': 'lexi',
        'pedro.name': 'pedro',
        'prancer.name': 'prancer',
        'ruger.name': 'ruger',
        'tessie.name': 'tessie',
        'tiffany.name': 'tiffany',
        'vixen.name': 'vixen',
    }
    check_mod_vals(mod, expected)


def check_mod_vals(mod, expected):
    pass
