import unittest

from splunge import app, util

class ValidateMethodTests(unittest.TestCase):
    def test_no_methods(self):
        method = "GET"
        methods = None
        self.assertFalse(util.validate_method(method, methods))

    def test_same(self):
        method = "GET"
        methods = "GET"
        self.assertTrue(util.validate_method(method, methods))

    def test_simple(self):
        method = "GET"
        methods = ["GET", "POST", "DELETE"]
        self.assertTrue(util.validate_method(method, methods))

    def test_simple_missing(self):
        method = "PUT"
        methods = ["GET", "POST", "DELETE"]
        self.assertFalse(util.validate_method(method, methods))

    def test_different(self):
        method = "GET"
        methods = "POST"
        self.assertFalse(util.validate_method(method, methods))

    def test_empty(self):
        method = None
        methods = [None, "GET", "POST"]
        self.assertFalse(util.validate_method(method, methods))