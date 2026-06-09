import os.path
import sys
import unittest
from markdown_it import MarkdownIt
from werkzeug.test import create_environ
from splunge import util
from splunge import Xgi

class Tests(unittest.TestCase):
	def test_add_code_folder(self):
		home = os.getenv('HOME')
		codeFolderPath = f"{home}/src/splunge/test/code"
		name = 'mycode'
		util.add_code_folder(name, codeFolderPath)
		self.assertIn(codeFolderPath, sys.path)
		self.assertIn(name, sys.modules)
		self.assertIn(codeFolderPath, sys.modules[name].__path__)


	def test_create_namespace_package(self):
		name = 'folder'
		path = "/tmp/blimpy"                                            # Choose a folder
		self.assertTrue(os.path.exists(path))
		nsPackage = util.create_namespace_package(name, path)
		self.assertIsNotNone(nsPackage)
		self.assertIsNotNone(sys.modules[name]) # Confirm the module was successfully added to `sys.modules`
	
	def test_get_spec_name_and_module_path(self):
		home = os.getenv('HOME')
		codeFolderPath = f"{home}/src/splunge/test/code"
		moduleName = "rel"
		codeFolderNspName = "mycode"
		expectedSpecName = f"{codeFolderNspName}.{moduleName}"
		expectedModulePath = f"{codeFolderPath}/{moduleName}.py"
		(spec_name, module_path) = util.get_spec_name_and_module_path(moduleName, codeFolderPath, codeFolderNspName)
		self.assertEqual(expectedSpecName, spec_name)
		self.assertEqual(expectedModulePath, module_path)

	def test_get_spec_name_and_module_path2(self):
		# home = os.getenv('HOME')
		moduleName="meat.foo"
		codeFolderPath=os.path.abspath("./www")
		codeFolderNspName = "codefolder"
		expectedSpecName = f"{codeFolderNspName}.{moduleName}"
		expectedModulePath = f"{codeFolderPath}/{'/'.join(moduleName.split('.'))}.py"
		(spec_name, module_path) = util.get_spec_name_and_module_path(moduleName, codeFolderPath, codeFolderNspName)
		self.assertEqual(expectedSpecName, spec_name)
		self.assertEqual(expectedModulePath, module_path)

	def test_html_fragment_to_doc(self):
		md = MarkdownIt()
		markdown = "### Content</p>\n<p>Hello!</p>\n"
		frag = md.render(markdown)
		doc = util.html_fragment_to_doc(frag)

	def test_is_index_page_empty_string(self):
		xgi = Xgi.create('')
		flag = xgi.is_index_page()
		self.assertTrue(flag)
	
	def test_is_index_page_slash(self):
		xgi = Xgi.create('/')
		flag = xgi.is_index_page()
		self.assertTrue(flag)

	def test_load_module(self):
		home = os.getenv('HOME')
		codeFolderPath = f"{home}/src/splunge/test/code"
		moduleName = "rel"
		codeFolderNspName = "mycode"
		mod = util.load_module(moduleName, codeFolderPath, codeFolderNspName)
		self.assertIsNotNone(mod)
		self.assertEqual(codeFolderNspName, mod.__package__)
		self.assertIn(codeFolderPath, sys.path)
		self.assertIn(codeFolderNspName, sys.modules)
		self.assertIn(codeFolderPath, sys.modules[codeFolderNspName].__path__)

	def test_load_module_spec(self):
		home = os.getenv('HOME')
		codeFolderPath = f"{home}/src/splunge/test/code"
		codeFolderNspName = "mycode"
		moduleName = "rel"
		spec = util.load_module_spec(moduleName, codeFolderPath, codeFolderNspName)
		self.assertIsNotNone(spec)
		