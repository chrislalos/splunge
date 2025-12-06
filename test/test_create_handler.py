import unittest
from werkzeug.test import create_environ
from splunge import app
from splunge import FileHandler, MarkdownHandler, PythonModuleHandler, SourceHandler
from splunge import Xgi

class CreateHandlerTests(unittest.TestCase):
    def test_module(self):
        test_handler(self, "/www/meat/foo", PythonModuleHandler)

    def test_markdown(self):
        test_handler(self, "/www/hello.md", MarkdownHandler)

    def test_python_source(self):
        print()
        handler = test_handler(self, "/www/meat/foo.py", SourceHandler)
        print(handler)
    
    def test_static_content(self):
        test_handler(self, "/www/hello.html", FileHandler)

def test_handler(t, path, handlerType):
    xgi = Xgi.create(path)
    handler = app.create_handler(xgi)
    t.assertIsNotNone(handler)
    t.assertIsInstance(handler, handlerType)
    return handler