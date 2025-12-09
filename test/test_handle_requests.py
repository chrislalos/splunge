import os
import os.path
import unittest
from werkzeug.test import create_environ
from splunge import app
from splunge import handlers, util, FileHandler, IndexPageHandler, MarkdownHandler, PythonModuleHandler, PythonTemplateHandler, Response, SourceHandler, Xgi

class HandleRequestTests(unittest.TestCase):
	def test_index_page(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, "", IndexPageHandler)
		# Test the response
		test_response_redirect(self, resp, '/index.html')

	def test_markdown(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, "/www/hello.md", MarkdownHandler)
		# Test the response
		test_response_ok_html(self, resp)

	def test_markup(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, "/www/meat/bar?name=meat", PythonTemplateHandler)
		# Test the response
		test_response_ok_html(self, resp)

	def test_module(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, "/www/meat/foo", PythonModuleHandler)
		# Test the response
		test_response_ok_html(self, resp)
		
	def test_module_plus_markup(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, "/www/meat/foo3", PythonModuleHandler)
		# Test the response
		test_response_ok_html(self, resp)
		
	def test_module_with_redirect(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, "/www/meat/redirect_0_from", PythonModuleHandler)
		# Test the response
		test_response_redirect(self, resp, 'redirect_0_to.html')

	def test_module_with_under(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, "/www/meat/foo2", PythonModuleHandler)
		# Test the response
		test_response_ok_html(self, resp)
	
	def test_python_source(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, '/www/meat/foo.py', SourceHandler)
		# Test the response
		test_response_ok_html(self, resp)

	def test_static_content_html(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, '/www/hello.html', FileHandler)
		# Test the response
		test_response_ok(self, resp, "text/html")

	def test_static_content_png(self):
		# Create a xgi, then create + execute a handler for it
		(handler, resp) = create_and_test_handler(self, '/www/img/sun.png', FileHandler)
		# Test the response
		test_response_ok(self, resp, "image/png")


def create_xgi(path):
	wsgi = create_environ(path)
	xgi = Xgi(wsgi)
	return xgi


def create_and_test_handler(t, path, handlerType):
	xgi = Xgi.create(path)
	handler = handlers.create(xgi)
	t.assertIsNotNone(handler)
	t.assertIsInstance(handler, handlerType)
	resp = handler.handle_request()
	t.assertIsNotNone(resp)
	return (handler, resp)


def test_response(t, resp, statusCode, contentType, location=None):
	t.assertIsNone(resp.exc_info)
	t.assertEqual(statusCode, resp.statusCode)
	t.assertEqual(contentType, resp.contentType)
	t.assertEqual(location, resp.location)


def test_response_ok(t, resp, contentType):
	test_response(t, resp, 200, contentType, None)
	t.assertTrue(int(resp.contentLength) > 0)


def test_response_ok_html(t, resp):
	test_response_ok(t, resp, "text/html; charset=utf-8")

def test_response_redirect(t, resp, location):
	test_response(t, resp, 303, None, location)
	t.assertTrue(int(resp.contentLength) == 0)
