import importlib
import os
import unittest
from werkzeug.test import create_environ

from splunge import util, EnrichedModule, ModuleExecutionResponse, Xgi

class ModuleFunctionTests(unittest.TestCase):
    def test_exec_module_check_stdout(self):
        ''' Confirm that util.load_module() does not initialize the module. '''
        path = '/modules/foo.py'
        modulePath = './test/modules/foo.py'
        xgi = Xgi.create(path)
        module = util.load_module_by_path(modulePath)
        self.assertIsNotNone(module)
        # module_state = ModuleExecutionResponse.exec_module(module)
        em = EnrichedModule(module, xgi)
        result = em.exec()
        self.assertIsNotNone(result)
        self.assertTrue('meat0' in result.context)
        self.assertEqual(result.context['meat0'], "meat")
        self.assertTrue(result.has_stdout())
        self.assertFalse(util.is_io_empty(result.stdout))
        output = result.get_stdout_value()
        self.assertIsNotNone(output)
        self.assertEqual(b'meat0=meat\n', output)


    def legacy_test_exec_module_check_stdout(self):
        ''' Confirm that util.load_module() does not initialize the module. '''
        path = './test/modules/foo.py'
        module = util.load_module_by_path(path)
        self.assertIsNotNone(module)
        module_state = ModuleExecutionResponse.exec_module(module)
        self.assertIsNotNone(module_state)
        val = module_state.context[0]["meat0"]
        self.assertEqual(val, "meat")
        output = module_state.stdout.getvalue()
        self.assertEqual("meat0=meat\n", output)


    def test_exec_module_check_underscore(self):
        ''' Confirm that util.load_module() does not initialize the module. '''
        path = './test/modules/bar.py'
        module = util.load_module_by_path(path)
        self.assertIsNotNone(module)
        module_state = ModuleExecutionResponse.exec_module(module)
        self.assertIsNotNone(module_state)
        val0 = module_state.context[0]["meat0"]
        val1 = module_state.context[0]["meat1"]
        val2 = module_state.context[0]["meat2"]
        self.assertEqual(val0, "meat")
        self.assertEqual(val1, "Meat!")
        self.assertEqual(val2, "MEAT!!!")

    def test_get_module_attrs(self):
        ''' '''
        path = './test/modules/foo.py'
        module = util.load_module_by_path(path)
        attrNames = util.get_attr_names(module)
        module_parent = importlib.import_module('test.modules')

    def test_load_module(self):
        path = './test/modules/foo.py'
        module = util.load_module_by_path(path)
        self.assertIsNotNone(module)

    def test_load_module_check_no_initialization(self):
        ''' Confirm that util.load_module() does not initialize the module. '''
        path = './test/modules/foo.py'
        module = util.load_module_by_path(path)
        self.assertIsNotNone(module)
        self.assertFalse(hasattr(module, 'meat0'))

    def test_load_module_spec(self):
        ''' Load a module spec from its path '''
        path = './test/modules/foo.py'
        spec = util.load_module_spec(path)
        self.assertIsNotNone(spec)
    
    def test_load_module_spec_no_file(self):
        ''' Load a non-existent module; confirm None '''
        path = './test/modules/fooXXX.py'
        spec = util.load_module_spec(path)
        self.assertIsNone(spec)
