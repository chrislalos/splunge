import contextlib
from http.cookies import SimpleCookie
import importlib
import inspect
import io
import os
import re
import sys
from importlib.machinery import FileFinder, SourceFileLoader
import urllib
from .mimetypes import mimemap
from typing import NamedTuple
from . import ModuleExecutionState
from . import util
from .handlers import PythonModuleHandler, PythonTemplateHandler


handler_map = {'application/x-python-code': "PythonSourceHandler",
               'application/x-splunge-template': "PythonTemplateHandler"
              }


def create_handler(wsgi):
	""" Return the appropriate handler for the wsgi. """
	if is_python_module(wsgi):
		return PythonModuleHandler()
	elif is_python_markup(wsgi):
		return PythonTemplateHandler()
	elif is_mime_type(wsgi):
		return util.create_mime_handler(wsgi)
	else:
		return "unknown"


def is_mime_type(wsgi):
	''' Check if the wsgi has a recognized MIME type. '''
	ext = util.get_path_extension(wsgi)
	flag = not not ext
	return ext


def is_python_markup(wsgi):
	''' Check if a request respresents python markup / jinja template.
	
	A request represents a python markup iff
		- Its path has no extension
		- Appending .pyp to the path yields a file that exists in the local
		  filesystem
	'''
	ext = util.get_path_extension(wsgi)
	local_path = util.get_local_path(wsgi)
	# Is the path a non-existent file *and* does it lack an extension? (e.g. http://foo.com/app/user)  
	if not ext and not os.path.isfile(local_path):
		templatePath = f'{local_path}.pyp'
		if os.path.isfile(templatePath):
			return True
	return False


def is_python_module(wsgi):
	''' Check if a request respresents a python module.
	
	A request represents a python module iff
		- Its path has no extension
		- Appending .py to the path yields a file that exists in the local
		  filesystem
	'''
	ext = util.get_path_extension(wsgi)
	local_path = util.get_local_path(wsgi)
	# Is the path a non-existent FILE and does it lack an extension? (e.g. http://foo.com/app/user)  
	if not ext and not os.path.isfile(local_path):
		# If it exists (as a file) when we append .py, use PythonHandler
		module_path = '.'.join([local_path, 'py'])
		if os.path.isfile(module_path):
			return True
	return False


def app(wsgi, start_response):
	"""Simplest possible application object"""
	handler = create_handler(wsgi)
	(resp, done) = handler.handle_request(wsgi)
	if done:
		status = resp.status
		headers = resp.headers.asTuples()
		data = resp.iter
		start_response(status, headers)
		return data
	# error
	data = b'no clue dude'
	status = '513 no clue dude'
	response_headers = [
		('Content-type', 'text/plain'),
		('Content-Length', str(len(data)))
	]
	start_response(status, response_headers)
	return iter([data])
