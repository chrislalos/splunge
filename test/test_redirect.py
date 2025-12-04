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
		print()
		url = "/meat/redirect_0_from"
		cli = Client(app.app)
		resp = cli.get(url)
		print(resp)
	