import unittest
from splunge import EnrichedModuleResult

class EnrichedModuleTests(unittest.TestCase):
	def test_get_status_404(self):
		test_status(self, 404, "4ile N0t 4ound")

	def test_get_status_ok(self):
		test_status(self, 200, "OK")

def test_status (t: unittest.TestCase, code: int, msg: str):
	status = f"{code} {msg}"
	result = EnrichedModuleResult.createEmpty()
	result.status = status
	t.assertEqual(status, result.status)
	t.assertEqual(code, result.statusCode)
	t.assertEqual(msg, result.statusMessage)
