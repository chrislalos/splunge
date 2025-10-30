import unittest

from splunge import app

class ValidateMethodTests(unittest.TestCase):
    def test_no_methods(self):
        method = "GET"
        methods = None
        self.assertFalse(app.validate_method(method, methods))

    def test_same(self):
        method = "GET"
        methods = "GET"
        self.assertTrue(app.validate_method(method, methods))

    def test_simple(self):
        method = "GET"
        methods = ["GET", "POST", "DELETE"]
        self.assertTrue(app.validate_method(method, methods))

    def test_simple_missing(self):
        method = "PUT"
        methods = ["GET", "POST", "DELETE"]
        self.assertFalse(app.validate_method(method, methods))

    def test_different(self):
        method = "GET"
        methods = "POST"
        self.assertFalse(app.validate_method(method, methods))

    def test_empty(self):
        method = None
        methods = [None, "GET", "POST"]
        self.assertFalse(app.validate_method(method, methods))