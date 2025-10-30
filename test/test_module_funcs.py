import importlib
import unittest

from splunge import util

class ModuleFunctionTests(unittest.TestCase):
    def test_exec_module_check_stdout(self):
        ''' Confirm that util.load_module() does not initialize the module. '''
        path = './test/modules/foo.py'
        module = util.load_module(path)
        self.assertIsNotNone(module)
        module_state = util.exec_module(module)
        self.assertIsNotNone(module_state)
        val = module_state.context["meat0"]
        self.assertEqual(val, "meat")
        output = module_state.stdout.getvalue()
        self.assertEqual("meat0=meat\n", output)

    def test_exec_module_check_underscore(self):
        ''' Confirm that util.load_module() does not initialize the module. '''
        path = './test/modules/bar.py'
        module = util.load_module(path)
        self.assertIsNotNone(module)
        module_state = util.exec_module(module)
        self.assertIsNotNone(module_state)
        val0 = module_state.context["meat0"]
        val1 = module_state.context["meat1"]
        val2 = module_state.context["meat2"]
        self.assertEqual(val0, "meat")
        self.assertEqual(val1, "Meat!")
        self.assertEqual(val2, "MEAT!!!")

    def test_get_module_attrs(self):
        ''' '''
        path = './test/modules/foo.py'
        module = util.load_module(path)
        attrNames = util.get_attr_names(module)
        module_parent = importlib.import_module('test.modules')

    def test_load_module(self):
        path = './test/modules/foo.py'
        module = util.load_module(path)
        self.assertIsNotNone(module)

    def test_load_module_check_no_initialization(self):
        ''' Confirm that util.load_module() does not initialize the module. '''
        path = './test/modules/foo.py'
        module = util.load_module(path)
        self.assertIsNotNone(module)
        self.assertFalse(hasattr(module, 'meat0'))

    def test_load_module_spec(self):
        path = './test/modules/foo.py'
        spec = util.load_module_spec(path)
        self.assertIsNotNone(spec)
    
    def test_load_module_spec_no_file(self):
        path = './test/modules/fooXXX.py'
        spec = util.load_module_spec(path)
        self.assertIsNone(spec)
