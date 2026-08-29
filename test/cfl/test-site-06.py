from splunge import CodeFolderLoader

import importlib
import pytest
import sys


@pytest.fixture(scope='module')
def loader():
    ldr = CodeFolderLoader(['/www/site-06'])
    ldr.install()
    yield ldr
    ldr.uninstall()



def test_import_bullwinkle(loader):
    mod = importlib.import_module('codefolder.bullwinkle')
    assert mod is not None
    expected = {
        'Indianapolis_Racers.latte.name': 'latte-san',
    }
    check_mod_vals(mod, expected)

def test_import_crystal(loader):
    mod = importlib.import_module('codefolder.Indianapolis_Racers.Jaxson.crystal')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)

def test_import_hello1(loader):
    mod = importlib.import_module('codefolder.hello1')
    assert mod is not None
    expected = {
        'rel1.name': 'rel1-san',
        'rel2.name': 'rel2-san',
        'rel3.name': 'rel3-san',
        'rel4.name': 'rel4-san',
        'bullwinkle.name': 'bullwinkle-san',
        'Scarolina_Panzers.rufus.name': 'rufus-san',
        'Indianapolis_Racers.latte.name': 'latte-san',
        'Indianapolis_Racers.Jaxson.crystal.name': 'crystal-san',
    }
    check_mod_vals(mod, expected)

def test_import_hello2(loader):
    mod = importlib.import_module('codefolder.Indianapolis_Racers.hello2')
    assert mod is not None
    expected = {
        'rel1.name': 'rel1-san',
        'rel2.name': 'rel2-san',
        'rel3.name': 'rel3-san',
        'rel4.name': 'rel4-san',
        'bullwinkle.name': 'bullwinkle-san',
        'Scarolina_Panzers.rufus.name': 'rufus-san',
        'Indianapolis_Racers.latte.name': 'latte-san',
        'Indianapolis_Racers.Jaxson.crystal.name': 'crystal-san',
    }
    check_mod_vals(mod, expected)

def test_import_hello3(loader):
    mod = importlib.import_module('codefolder.Indianapolis_Racers.Jaxson.hello3')
    assert mod is not None
    expected = {
        'rel1.name': 'rel1-san',
        'rel2.name': 'rel2-san',
        'rel3.name': 'rel3-san',
        'rel4.name': 'rel4-san',
        'bullwinkle.name': 'bullwinkle-san',
        'Scarolina_Panzers.rufus.name': 'rufus-san',
        'Indianapolis_Racers.latte.name': 'latte-san',
        'Indianapolis_Racers.Jaxson.crystal.name': 'crystal-san',
    }
    check_mod_vals(mod, expected)

def test_import_latte(loader):
    mod = importlib.import_module('codefolder.Indianapolis_Racers.latte')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)

def test_import_rel1(loader):
    mod = importlib.import_module('codefolder.rel1')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)

def test_import_rel2(loader):
    mod = importlib.import_module('codefolder.Scarolina_Panzers.rel2')
    assert mod is not None
    expected = {
        'rel3.name': 'rel3-san',
        'Indianapolis_Racers.latte.name': 'latte-san',
    }
    check_mod_vals(mod, expected)

def test_import_rel3(loader):
    mod = importlib.import_module('codefolder.Indianapolis_Racers.rel3')
    assert mod is not None
    expected = {
        'rel1.name': 'rel1-san',
        'Scarolina_Panzers.rufus.name': 'rufus-san',
        'bullwinkle.name': 'bullwinkle-san',
    }
    check_mod_vals(mod, expected)

def test_import_rel4(loader):
    mod = importlib.import_module('codefolder.Indianapolis_Racers.Jaxson.rel4')
    assert mod is not None
    expected = {
        'rel1.name': 'rel1-san',
        'Indianapolis_Racers.Jaxson.crystal.name': 'crystal-san',
    }
    check_mod_vals(mod, expected)

def test_import_rufus(loader):
    mod = importlib.import_module('codefolder.Scarolina_Panzers.rufus')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)



def check_mod_vals(mod, expected):
    for key, val in expected.items():
        obj = mod
        for part in key.split('.'):
            obj = getattr(obj, part)
        assert obj == val, f'{key}: expected {val!r}, got {obj!r}'
