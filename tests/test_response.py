import unittest
from splunge import Headers, Response

class ResponseTests(unittest.TestCase):
	def test_init (self):
		resp = Response()
		self.assertEqual(200, resp.statusCode)
		self.assertEqual("OK", resp.statusMessage)
		self.assertEqual('200 OK', resp.status)
		self.assertIsNotNone(resp.headers)
		self.assertEqual(0, len(resp.headers))
		self.assertIsNone(resp.exc_info)
		self.assertIsNotNone(resp.iter)
		self.assertEqual(0, len(resp.iter))

	def test_redirect(self):
		resp = Response()
		url = "http://example.com/newurl"
		resp.redirect(url)
		self.assertEqual(303, resp.statusCode)
		self.assertEqual(f'Redirecting to {url}', resp.statusMessage)
		self.assertEqual(1, len(resp.headers.items()))
		locationHeader = resp.headers['Location']
		self.assertIsNotNone(locationHeader)
		self.assertEqual(url, locationHeader)

