import os
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.dirname(__file__))
import util

class Tests(unittest.TestCase):
	proc = None
	sock_path = None
	_prev_cwd = None
	_tmp_dir = None

	@classmethod
	def setUpClass(cls):
		cls._prev_cwd = os.getcwd()
		os.chdir(util.WWW_DIR)
		cls._tmp_dir = tempfile.mkdtemp(prefix='splunge.test.')
		cls.sock_path = os.path.join(cls._tmp_dir, 'splunge.sock')
		cls.proc = util.start_server(
			'runSplungeOnUnixSocket', cls.sock_path,
			env={
                'SPLUNGE_TEMPLATE_FOLDER': './templates',
                'SPLUNGE_CODEFOLDER': '.',
            },
		)
		util.wait_for_socket(cls.sock_path)

	@classmethod
	def tearDownClass(cls):
		util.stop_server(cls.proc)
		if cls._prev_cwd:
			os.chdir(cls._prev_cwd)

	def test_404(self):
		status, _ = util.socket_get(self.sock_path, '/does/not/exist')
		self.assertEqual(404, status)

	def test_hello_html(self):
		status, body = util.socket_get(self.sock_path, '/hello.html')
		self.assertEqual(200, status)
		self.assertIn('🌞', body)

	def test_hello_md(self):
		status, body = util.socket_get(self.sock_path, '/hello.md')
		self.assertEqual(200, status)
		self.assertIn('helloooo', body)

	def test_meat_foo(self):
		status, body = util.socket_get(self.sock_path, '/meat/foo')
		self.assertEqual(200, status)
		self.assertIn('Hi everybody', body)

	def test_meat_foo3(self):
		status, body = util.socket_get(self.sock_path, '/meat/foo3')
		self.assertEqual(200, status)
		self.assertIn('MEAT', body)
