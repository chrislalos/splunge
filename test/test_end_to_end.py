import os
import unittest
from werkzeug import Client
from splunge import app, Response

CT_html = "text/html; charset=utf-8"

class Tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.cwdPrev = os.getcwd()
		os.chdir('/www')

	@classmethod
	def tearDownClass(cls):
		os.chdir(cls.cwdPrev)

	def test_404(self):
		url = "/xxx/yyy/zzz"
		cli = Client(app.app)
		resp = cli.get(url)
		statusCode, sep, statusMessage = resp.status.partition(' ')
		self.assertEqual(str(404), statusCode)
		if statusMessage:
			self.assertNotEqual('OK', statusMessage.upper())


	def test_hello_html(self):
		check_get(self, "/hello.html", contentType=constants.MT_html, contentLength=os.path.getsize("hello.html"))

	def test_hello_bar(self):
		check_get(self, "/hello/bar", contentType=CT_html)

	def test_hello_foo(self):
		check_get(self, "/hello/foo", contentType=CT_html)

	def test_hello_foo3_pyp(self):
		check_get(self, "/hello/foo3.pyp", contentType=CT_html)

	def test_new_rel(self):
		pass

	def test_rel(self):
		check_get(self, "/rel", contentType=CT_html)


def check_get(t: unittest.TestCase, url: str, *, contentType=None, contentLength=None) -> Response: 
	cli = Client(app.app)
	resp = cli.get(url)
	statusCode, sep, statusMessage = resp.status.partition(' ')
	t.assertEqual(str(200), statusCode)
	if statusMessage:
		t.assertEqual('OK', statusMessage.upper())
	t.assertIsNotNone(resp.content_length)
	if contentLength:
		t.assertEqual(contentLength, resp.content_length)
	else:
		t.assertTrue(resp.content_length > 0)
	if contentType:
		t.assertEqual(contentType, resp.content_type)
	return resp
