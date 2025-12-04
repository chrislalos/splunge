import os
import unittest
from werkzeug import Client
from splunge import app
class RedirectTests(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.cwd = os.getcwd()
		os.chdir('./www')

	@classmethod
	def tearDownClass(cls):
		os.chdir(cls.cwd)

	def test_to_html(self):
		url = "/meat/redirect_0_from"
		test_redirect(self, url)
	
	def test_to_template(self):
		url = "/meat/redirect_1_from"
		test_redirect(self, url)


def test_redirect(t: unittest.TestCase, url: str):
	cli = Client(app.app)
	resp = cli.get(url)
	t.assertEqual(303, resp.status_code)
	t.assertEqual(0, resp.content_length)
	t.assertIsNone(resp.content_type)
	t.assertIsNotNone(resp.location)
	
