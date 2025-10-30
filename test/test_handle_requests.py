import os
import os.path
import unittest
from werkzeug.test import create_environ
from splunge import app
from splunge import PythonModuleHandler, PythonTemplateHandler
from splunge import util
from splunge import Response

class HandleRequestTests(unittest.TestCase):
	def test_markup(self):
		# Create a wsgi + then create a handler for it
		wsgi = create_environ("/www/meat/bar?name=meat")
		handler = app.create_handler(wsgi)
		self.assertIsNotNone(handler)
		self.assertIs(type(handler), PythonTemplateHandler)
		# Execute the handler
		(resp, isDone) = handler.handle_request(wsgi)
		self.assertIsNotNone(resp)
		self.assertIs(type(resp), Response)
		self.assertTrue(isDone)
		# Test the response
		self.assertIsNone(resp.exc_info)

	def test_module(self):
		# Create a wsgi + then create a handler for it
		wsgi = create_environ("/www/meat/foo")
		handler = app.create_handler(wsgi)
		self.assertIsNotNone(handler)
		self.assertIs(type(handler), PythonModuleHandler)
		# Execute the handler
		(resp, isDone) = handler.handle_request(wsgi)
		self.assertIsNotNone(resp)
		self.assertIsNotNone(isDone)
		self.assertIs(type(resp), Response)
		self.assertTrue(isDone)
		# Test the response
		self.assertIsNone(resp.exc_info)

	def test_module_plus_markup(self):
		# Create a wsgi + then create a handler for it
		wsgi = create_environ("/www/meat/foo3")
		handler = app.create_handler(wsgi)
		self.assertIsNotNone(handler)
		self.assertIs(type(handler), PythonModuleHandler)
		# Execute the handler
		(resp, isDone) = handler.handle_request(wsgi)
		self.assertIsNotNone(resp)
		self.assertIsNotNone(isDone)
		self.assertIs(type(resp), Response)
		self.assertTrue(isDone)
		# Test the response
		self.assertIsNone(resp.exc_info)

	def test_module_with_under(self):
		# Create a wsgi + then create a handler for it
		wsgi = create_environ("/www/meat/foo2")
		handler = app.create_handler(wsgi)
		self.assertIsNotNone(handler)
		self.assertIs(type(handler), PythonModuleHandler)
		# Execute the handler
		(resp, isDone) = handler.handle_request(wsgi)
		self.assertIsNotNone(resp)
		self.assertIsNotNone(isDone)
		self.assertIs(type(resp), Response)
		self.assertTrue(isDone)
		# Test the response
		self.assertIsNone(resp.exc_info)

	def test_get_local_path(self):
		wsgi = create_environ("/meat/foo")

