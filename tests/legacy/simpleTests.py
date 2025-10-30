import unittest

class C:
	def __init__ (self, x):
		self.x = x

	@property
	def X (self):
		return self.x

class Test (unittest.TestCase):
	def testSomething (self):
		c = C(13)
		self.assertEqual(c.x, 13)
		self.assertEqual(c.X, 13)
