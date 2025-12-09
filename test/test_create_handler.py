import unittest
from werkzeug.test import create_environ
from splunge import app
from splunge import handlers
from splunge.handlers import FileHandler, HtmlGenHandler, IndexPageHandler, MarkdownHandler, PythonModuleHandler, PythonTemplateHandler, SourceHandler
from splunge import Xgi

class CreateHandlerTests(unittest.TestCase):
	def test_index(self):
		test_handler(self, '/', IndexPageHandler)
		pass

	def test_mime_types(self):
		mimeType = "text/html; charset=utf-8"
		xgi = Xgi.create("/")
		self.assertEqual(mimeType, SourceHandler(xgi).get_mime_type())
		self.assertEqual(mimeType, PythonTemplateHandler(xgi).get_mime_type())
		self.assertEqual(mimeType, MarkdownHandler(xgi).get_mime_type())


	def test_module(self):
		test_handler(self, "/www/meat/foo", PythonModuleHandler)

	def test_markdown(self):
		test_handler(self, "/www/hello.md", MarkdownHandler)

	def test_python_source(self):
		test_handler(self, "/www/meat/foo.py", SourceHandler)
	
	def test_pyp_source(self):
		handler = test_handler(self, "/www/meat/foo3.pyp", SourceHandler)
	
	def test_static_content(self):
	    test_handler(self, "/www/hello.html", FileHandler)


def test_handler(t, path, handlerType):
	xgi = Xgi.create(path)
	handler = handlers.create(xgi)
	t.assertIsNotNone(handler)
	t.assertIsInstance(handler, handlerType)
	return handler