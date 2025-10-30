import unittest
from werkzeug.test import create_environ
from splunge import app
from splunge import PythonModuleHandler

class CreateHandlerTests(unittest.TestCase):
    def test_module(self):
        wsgi = create_environ("/www/meat/foo")
        handler = app.create_handler(wsgi)
        self.assertIsNotNone(handler)
        self.assertIs(type(handler), PythonModuleHandler)