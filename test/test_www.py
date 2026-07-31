import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(__file__))
import util

class Tests(unittest.TestCase):
	proc = None
	port = None

	@classmethod
	def setUpClass(cls):
		cls.port = util.find_free_port()
		cls.proc = util.start_server(
			'www', cls.port, util.WWW_DIR,
			env={
                'SPLUNGE_TEMPLATE_FOLDER': './templates',
                'SPLUNGE_CODEFOLDER': '.',
            },
		)
		util.wait_for_port(cls.port)

	@classmethod
	def tearDownClass(cls):
		util.stop_server(cls.proc)

	def test_404(self):
		status, _ = util.http_get(self.port, '/does/not/exist')
		self.assertEqual(404, status)

	def test_hello_html(self):
		status, body = util.http_get(self.port, '/hello.html')
		self.assertEqual(200, status)
		self.assertIn('🌞', body)

	def test_hello_bar(self):
		status, body = util.http_get(self.port, '/hello/bar')
		self.assertEqual(200, status)

	def test_hello_foo(self):
		status, body = util.http_get(self.port, '/hello/foo')
		self.assertEqual(200, status)
		self.assertIn('Hi everybody', body)

	def test_hello_foo3_pyp(self):
		status, body = util.http_get(self.port, '/hello/foo3')
		self.assertEqual(200, status)
		self.assertIn('MEAT', body)

	def test_new_rel(self):
		pass

	def test_rel(self):
		status, body = util.http_get(self.port, '/rel')
		self.assertEqual(200, status)
