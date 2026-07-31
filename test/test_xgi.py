import os.path
import unittest
from splunge import Xgi

class Tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		home = os.getenv('HOME')
		cls.codeFolder = f"{home}/src/splunge/test/code"
		cls.oldCwd = os.getcwd()
		os.chdir(cls.codeFolder)

	@classmethod
	def tearDownClass(cls):
		os.chdir(cls.oldCwd)

	def test_create_args(self):
		path = "/www/hello/bar?name=meat"
		xgi = Xgi.create(path)
		# get args
		getArgs = xgi.create_get_args()
		self.assertIsNotNone(getArgs)
		self.assertEqual(1, len(getArgs))
		self.assertTrue('name' in getArgs)
		self.assertEqual("meat", getArgs['name'])
		# post args
		postArgs = xgi.create_post_args()
		self.assertIsNotNone(postArgs)
		# args
		self.assertEqual(0, len(postArgs))
		args = xgi.create_args()
		self.assertIsNotNone(args)
		self.assertEqual(1, len(args))
		self.assertTrue('name' in args)
		self.assertEqual("meat", args['name'])

	def test_get_module_path(self):
		path = '/rel'
		xgi = Xgi.create(path)
		self.assertIsNotNone(xgi)
		module_path = xgi.get_module_path(self.codeFolder)
		flag = os.path.exists(module_path)
		print(f'module_path={module_path}')
		self.assertTrue(flag)

	def test_is_python_module(self):
		path = '/foo'
		xgi = Xgi.create(path)
		self.assertIsNotNone(xgi)
		isModule = xgi.is_python_module(self.codeFolder)
		self.assertTrue(isModule)

	def test_is_python_module2(self):
		path = '/sub/bum'
		xgi = Xgi.create(path)
		self.assertIsNotNone(xgi)
		isModule = xgi.is_python_module(self.codeFolder)
		self.assertTrue(isModule)
