import contextlib
from io import StringIO
import os
import unittest
from werkzeug.test import create_environ
from splunge.HttpEnricher import HttpEnricher, create_enrichment_object, enrich_module
from splunge import util

def create_enricher (path, queryString=None):
	queryString="bar=13&bum=thirteen"
	wsgi = create_environ(path, query_string=queryString)
	http = HttpEnricher(wsgi)
	return http


class EnrichmentTests(unittest.TestCase):
	def test_enrich_module(self):
		path = './www/meat/foo.py'
		module = util.load_module(path)
		self.assertIsNotNone(module)
		self.assertFalse(hasattr(module, 'http'))
		wsgi = create_environ(path, method="GET")
		enrich_module(module, wsgi)
		self.assertTrue(hasattr(module, 'http'))
		http = getattr(module, "http")
		self.assertIsNotNone(http)
		self.assertIs(HttpEnricher, type(http))
		contentLength = 13
		http.set_content_length(contentLength)
		self.assertEqual(1, len(http.resp.headers.items()))
		headerValue = int(http.resp.headers['Content-Length'])
		self.assertIsNotNone(headerValue)
		self.assertEqual(contentLength, headerValue)
		
	def test_execute_module_foo(self):
		path = './www/meat/foo.py'
		module = util.load_module(path)
		wsgi = create_environ(path, method="GET")
		enrich_module(module, wsgi)
		moduleState = util.exec_module(module)
		self.assertIsNotNone(moduleState)
		self.assertEqual(1, len(moduleState.context))
		self.assertIsNotNone(moduleState.stdout)
		self.assertTrue(util.is_io_empty(moduleState.stdout))

	def test_module_args_get(self):
		http = create_enricher("/meat/foo", "bar=13&bum=thirteen")
		self.assertIsNotNone(http.args)
		self.assertEqual(str(13), http.args['bar'])
		self.assertEqual('thirteen', http.args['bum'])

	def test_module_args_post(self):
		http = create_enricher("/meat/foo", {'bar': 13, 'bum': 'thirteen'})
		self.assertIsNotNone(http.args)
		self.assertEqual(str(13), str(http.args['bar']))
		self.assertEqual('thirteen', http.args['bum'])

	def test_module_args_post_binary(self):
		path = "/meat/foo"
		b=b'0123456789'
		contentType='application/octet-stream'
		wsgi = create_environ(path, method="POST", data=b, content_type=contentType)
		self.assertEqual(contentType, wsgi['CONTENT_TYPE'])
		self.assertEqual(str(len(b)), wsgi['CONTENT_LENGTH'])
		http = HttpEnricher(wsgi)
		self.assertEqual(0, len(http.args))

	def test_module_local_path(self):
		path = "/www/meat/foo"
		wsgi = create_environ(path)
		localPath = util.get_local_path(wsgi)
		currDir = os.getcwd()
		self.assertEqual(f'{currDir}{path}', localPath)
		modulePath = f'{localPath}.py'
		self.assertTrue(os.path.isfile(modulePath))
		module = util.load_module(modulePath)
		self.assertIsNotNone(module)
		self.assertFalse(hasattr(module, 'meat'))

	def test_module_pypinfo(self):
		path = "/meat/foo"
		wsgi = create_environ(path)
		http = HttpEnricher(wsgi)
		stdout = StringIO()
		with contextlib.redirect_stdout(stdout):
			http.pypinfo()
		self.assertFalse(util.is_io_empty(stdout))

	def test_module_set_content_length(self):
		path = "/meat/foo"
		wsgi = create_environ(path)
		http = HttpEnricher(wsgi)
		contentLength = 13
		http.set_content_length(contentLength)
		self.assertEqual(1, len(http.resp.headers.items()))
		headerValue = int(http.resp.headers['Content-Length'])
		self.assertIsNotNone(headerValue)
		self.assertEqual(contentLength, headerValue)


	def test_module_set_content_type(self):
		path = "/meat/foo"
		wsgi = create_environ(path)
		http = HttpEnricher(wsgi)
		url = "http://example.com/newurl"
		contentType = "text/plain"
		http.set_content_type(contentType)
		self.assertEqual(1, len(http.resp.headers.items()))
		headerValue = http.resp.headers['Content-Type']
		self.assertIsNotNone(headerValue)
		self.assertEqual(contentType, headerValue)


	def test_module_validate_method(self):
		path = "/meat/foo"
		wsgi = create_environ(path)
		http = HttpEnricher(wsgi)
		method = "get"
		methods = ["pOSt", "gET"]
		self.assertTrue(http.validate_method(method, methods))
