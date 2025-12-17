import os
import unittest
from splunge import EnrichedModule, EnrichedModuleResult, Xgi

class Tests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.cwd = os.getcwd()
		os.chdir('./www')

	@classmethod
	def tearDownClass(cls):
		os.chdir(cls.cwd)

	def test_get_status_404(self):
		test_status(self, 404, "4ile N0t 4ound")

	def test_get_status_ok(self):
		test_status(self, 200, "OK")

	def test_get_args(self):
		xgi = Xgi.create("/meat/foo?name=meat")
		mod = EnrichedModule.create(xgi)
		self.assertIsNotNone(mod.http.args)
		self.assertEqual(1, len(mod.http.args))
		self.assertTrue('name' in mod.http.args)
		self.assertEqual('meat', mod.http.args['name'])


def test_status (t: unittest.TestCase, code: int, msg: str):
	status = f"{code} {msg}"
	result = EnrichedModuleResult.createEmpty()
	result.status = status
	t.assertEqual(status, result.status)
	t.assertEqual(code, result.statusCode)
	t.assertEqual(msg, result.statusMessage)
