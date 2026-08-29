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
        'billieName': 'billie',
        'blitzenName': 'blitzen',
        'brownieName': 'brownie',
        'cometName': 'comet',
        'cupidName': 'cupid',
        'dakotaName': 'dakota',
        'dancerName': 'dancer',
        'dasherName': 'dasher',
        'dollyName': 'dolly',
        'donnerName': 'donner',
        'ernieName': 'ernie',
        'isabellaName': 'isabella',
        'ivyName': 'ivy',
        'kobaName': 'koba',
        'lexiName': 'lexi',
        'pedroName': 'pedro',
        'prancerName': 'prancer',
        'rugerName': 'ruger',
        'tessieName': 'tessie',
        'tiffanyName': 'tiffany',
        'vixenName': 'vixen',
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
        'name': 'hello',
    }
    check_mod_vals(mod, expected)


def test_import_billie(loader):
    mod = importlib.import_module('codefolder.The_Harlem_Heroes.Miami_Thunder.New_New_York_Mets.billie')
    assert mod is not None
    expected = {
		'dolly.name': 'dolly',
		'tessie.name': 'tessie',
		'pedro.name': 'pedro',
		'isabella.name': 'isabella',
    }
    check_mod_vals(mod, expected)


def test_import_blitzen(loader):
    mod = importlib.import_module('codefolder.blitzen')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_brownie(loader):
    mod = importlib.import_module('codefolder.Boston_Minutemen.Whopping_Street_Wanderers.Boston_Whalers.brownie')
    assert mod is not None
    expected = {
		'koba.name': 'koba',
		'isabella.name': 'isabella',
		'pedro.name': 'pedro',
    }
    check_mod_vals(mod, expected)

def test_import_comet(loader):
    mod = importlib.import_module('codefolder.comet')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_cupid(loader):
    mod = importlib.import_module('codefolder.cupid')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_dakota(loader):
    mod = importlib.import_module('codefolder.Duluth_Bulldogs.Chicago_Talons.San_Francisco_Miners.dakota')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_dancer(loader):
    mod = importlib.import_module('codefolder.dancer')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_dasher(loader):
    mod = importlib.import_module('codefolder.dasher')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_dolly(loader):
    mod = importlib.import_module('codefolder.Washington_Punishers.Indianapolis_Rays.Ohio_Red_Dogs.dolly')
    assert mod is not None
    expected = {
		'ivy.name': 'ivy',
		'tiffany.name': 'tiffany',
    }


def test_import_donner(loader):
    mod = importlib.import_module('codefolder.donner')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_ernie(loader):
    mod = importlib.import_module('codefolder.The_Harlem_Heroes.Miami_Thunder.New_New_York_Mets.ernie')
    assert mod is not None
    expected = {
		'dakota.name': 'dakota',
		'dolly.name': 'dolly',
    }
    check_mod_vals(mod, expected)


def test_import_isabella(loader):
    mod = importlib.import_module('codefolder.Duluth_Bulldogs.Monroeville_Zombies.isabella')
    assert mod is not None
    expected = {
		'billie.name': 'billie',
		'ivy.name': 'ivy',
		'koba.name': 'koba',
		'lexi.name': 'lexi',
		'tessie.name': 'tessie',
    }
    check_mod_vals(mod, expected)


def test_import_ivy(loader):
    mod = importlib.import_module('codefolder.Duluth_Bulldogs.Monroeville_Zombies.ivy')
    assert mod is not None
    expected = {
		'brownie.name': 'brownie',
		'koba.name': 'koba',
		'tessie.name': 'tessie',
		'tiffany.name': 'tiffany',
    }
    check_mod_vals(mod, expected)


def test_import_koba(loader):
    mod = importlib.import_module('codefolder.Duluth_Bulldogs.Chicago_Talons.San_Francisco_Miners.koba')
    assert mod is not None
    expected = {
        'pedro.name': 'pedro',
        'billie.name': 'billie',
    }
    check_mod_vals(mod, expected)


def test_import_lexi(loader):
    mod = importlib.import_module('codefolder.Duluth_Bulldogs.Chicago_Talons.Korean_Invasion.lexi')
    assert mod is not None
    expected = {
        'ivy.name': 'ivy',
        'ruger.name': 'ruger',
        'ernie.name': 'ernie',
        'isabella.name': 'isabella',
        'billie.name': 'billie',
    }
    check_mod_vals(mod, expected)


def test_import_pedro(loader):
    mod = importlib.import_module('codefolder.The_Harlem_Heroes.Miami_Thunder.New_New_York_Mets.pedro')
    assert mod is not None
    expected = {
        'ernie.name': 'ernie',
        'isabella.name': 'isabella',
        'ivy.name': 'ivy',
    }
    check_mod_vals(mod, expected)


def test_import_prancer(loader):
    mod = importlib.import_module('codefolder.prancer')
    assert mod is not None
    expected = {
    }
    check_mod_vals(mod, expected)


def test_import_ruger(loader):
    mod = importlib.import_module('codefolder.Washington_Punishers.London_Silly_Nannies.Big_Green.ruger')
    assert mod is not None
    expected = {
		'koba.name': 'koba',
		'tiffany.name': 'tiffany',
    }
    check_mod_vals(mod, expected)


def test_import_tessie(loader):
    mod = importlib.import_module('codefolder.Boston_Minutemen.Rump_City_Bootyheads.Pelotillehue_Unido.tessie')
    assert mod is not None
    expected = {
        'dolly.name': 'dolly',
        'dakota.name': 'dakota',
    }
    check_mod_vals(mod, expected)


def test_import_tiffany(loader):
    mod = importlib.import_module('codefolder.Boston_Minutemen.Rump_City_Bootyheads.Pelotillehue_Unido.tiffany')
    assert mod is not None
    expected = {
        'koba.name': 'koba',
        'tessie.name': 'tessie',
        'dakota.name': 'dakota',
        'ivy.name': 'ivy',
        'lexi.name': 'lexi',
    }
    check_mod_vals(mod, expected)


def test_import_vixen(loader):
    mod = importlib.import_module('codefolder.vixen')
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
