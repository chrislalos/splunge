import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(__file__))
import util

class Tests(unittest.TestCase):
	proc = None
	port = None
	_prev_cwd = None

	@classmethod
	def setUpClass(cls):
		cls._prev_cwd = os.getcwd()
		os.chdir(util.WWW_DIR)
		cls.port = util.find_free_port()
		cls.proc = util.start_server(
			'runSplungeOnPort', cls.port,
			env={
                'SPLUNGE_TEMPLATE_FOLDER': './templates',
                'SPLUNGE_CODEFOLDER': '.',
            },
		)
		util.wait_for_port(cls.port)

	@classmethod
	def tearDownClass(cls):
		util.stop_server(cls.proc)
		if cls._prev_cwd:
			os.chdir(cls._prev_cwd)

	def test_404(self):
		status, _ = util.http_get(self.port, '/does/not/exist')
		self.assertEqual(404, status)

	def test_hello_html(self):
		status, body = util.http_get(self.port, '/hello.html')
		self.assertEqual(200, status)
		self.assertIn('🌞', body)

	def test_hello_md(self):
		status, body = util.http_get(self.port, '/hello.md')
		self.assertEqual(200, status)
		self.assertIn('helloooo', body)

	def test_meat_foo(self):
		status, body = util.http_get(self.port, '/meat/foo')
		self.assertEqual(200, status)
		self.assertIn('Hi everybody', body)

	def test_meat_foo3(self):
		status, body = util.http_get(self.port, '/meat/foo3')
		self.assertEqual(200, status)
		self.assertIn('MEAT', body)
