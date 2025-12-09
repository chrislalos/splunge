import os
import unittest
from werkzeug import Client
from splunge import app, Response

CT_html = "text/html; charset=utf-8"

class EndToEndTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.cwd = os.getcwd()
		os.chdir('./www')

	@classmethod
	def tearDownClass(cls):
		os.chdir(cls.cwd)

	def test_404(self):
		url = "/xxx/yyy/zzz"
		cli = Client(app.app)
		resp = cli.get(url)
		statusCode, sep, statusMessage = resp.status.partition(' ')
		self.assertEqual(str(404), statusCode)
		if statusMessage:
			self.assertNotEqual('OK', statusMessage.upper())


	def test_hello_html(self):
		test_get(self, "/hello.html", contentType="text/html", contentLength=os.path.getsize("hello.html"))


	def test_meat_bar(self):
		test_get(self, "/meat/bar", contentType=CT_html)

	def test_meat_foo(self):
		test_get(self, "/meat/foo", contentType=CT_html)

	def test_meat_foo3_pyp(self):
		test_get(self, "/meat/foo3.pyp", contentType=CT_html)


def test_get(t: unittest.TestCase, url: str, *, contentType=None, contentLength=None) -> Response: 
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
