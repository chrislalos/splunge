import unittest
from werkzeug.test import create_environ
from splunge import app
from splunge import FileHandler, PythonModuleHandler

class CreateHandlerTests(unittest.TestCase):
    def test_module(self):
        wsgi = create_environ("/www/meat/foo")
        handler = app.create_handler(wsgi)
        self.assertIsNotNone(handler)
        self.assertIs(type(handler), PythonModuleHandler)

    def test_static_content(self):
        wsgi = create_environ("/www/hello.html")
        handler = app.create_handler(wsgi)
        self.assertIsNotNone(handler)
        self.assertIs(type(handler), FileHandler)
    