import contextlib
import html
from http.cookies import SimpleCookie
import importlib
import inspect
import io
import os
import re
import sys
from importlib.machinery import FileFinder, SourceFileLoader
import traceback
import urllib
from typing import NamedTuple
from .mimetypes import mimemap
from . import ModuleExecutionResponse
from . import loggin, util
from .handlers import FileHandler, IndexPageHandler, PythonModuleHandler, PythonTemplateHandler, create_mime_handler
from .Headers import Headers
from .Response import Response


handler_map = {'application/x-python-code': "PythonSourceHandler",
               'application/x-splunge-template': "PythonTemplateHandler"
              }


def create_handler(wsgi):
	""" Return the appropriate handler for the wsgi. """
	handler = None
	if util.is_index_page(wsgi):
		handler =  IndexPageHandler()
	elif is_python_module(wsgi):
		handler = PythonModuleHandler()
	elif is_python_markup(wsgi):
		handler =  PythonTemplateHandler()
	elif is_mime_type(wsgi):
		handler = create_mime_handler(wsgi)
	else:
		handler = FileHandler()
	
	if handler:
		loggin.debug(f'handler found: {type(handler).__name__}')
	else:
		loggin.warning('no handler found')
	return handler


def is_mime_type(wsgi):
	''' Check if the wsgi has a recognized MIME type. '''
	ext = util.get_path_extension(wsgi)
	loggin.debug(f"is_mime_type(): ext={ext}")
	flag = ext in mimemap
	loggin.debug(f"is_mime_type(): flag={flag}")
	return flag


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


def handle_404(wsgi, start_response):
	loggin.debug("inside handle_404()")
	status = "404 Resource Not Found"
	templatePath = os.path.abspath(f'{os.getcwd()}/err/404.pyp')
	loggin.debug(f'templatePath={templatePath}')
	# Load the template & render it w wsgi args
	if not os.path.exists(templatePath):
		raise Exception(f'template path not found: {templatePath}')
	args = {"path": wsgi['PATH_INFO']}
	content = util.render_template(templatePath, args).encode()
	contentLength = len(content)
	headers = Headers()
	headers.contentLength = contentLength
	headers.contentType = "text/html"
	loggin.debug("headers")
	loggin.debug(headers)
	loggin.debug("starting response")
	start_response(status, headers.asTuples())
	return [content]


def handle_error(ex, wsgi, start_response):
	loggin.error(ex, exc_info=True)
	status = "513 uhoh"
	# data = f'oh no: {str(ex)}'.encode()
	# resp.contentLength = len(data)
	# headers = resp.headers.asTuples()
	templatePath = os.path.abspath(f'{os.getcwd()}/err/500.pyp')
	# Load the template & render it w wsgi args
	if not os.path.exists(templatePath):
		raise Exception(f'template path not found: {templatePath}')
	ss = traceback.extract_tb(ex.__traceback__)
	s = "".join([html.escape(line).lstrip() for line in ss.format()])
	args = {
		"message": str(ex),
		"traceback": s
	}
	content = util.render_template(templatePath, args).encode('utf-8')
	contentLength = len(content)
	headers = Headers()
	headers.contentLength = contentLength
	headers.contentType = "text/html"
	start_response(status, headers.asTuples())
	return [content]


def app(wsgi, start_response):
	resp = None
	try:
		loggin.debug(f"PATH_INFO={wsgi['PATH_INFO']}")
		loggin.debug(f"SCRIPT_NAME={wsgi['SCRIPT_NAME']}")
		loggin.debug(f"wsgi.file_wrapper={getattr(wsgi, 'file_wrapper', 'N/A')}")
		handler = create_handler(wsgi)
		respData = handler.handle_request(wsgi)
		loggin.debug(f'respData={respData}')
		(resp, done) = respData
	except FileNotFoundError as ex:
		loggin.error(f"404 - {wsgi['PATH_INFO']}")
		loggin.error(ex, exc_info=True)
		return handle_404(wsgi, start_response)
	except Exception as ex:
		loggin.warning('error caught in app()')
		return handle_error(ex, wsgi, start_response)
	if done:
		status = resp.status
		headers = resp.headers.asTuples() 
		data = resp.iter
		start_response(status, headers)
		# loggin.debug(f"len(data)={len(data)}")
		# loggin.debug(f"len(data[0])={len(data[0])}")
		return data
	# error
	data = b'no clue dude'
	status = '513 no clue dude'
	response_headers = [
		(Headers.HN_ContentLength, str(len(data))),
		(Headers.HN_ContentType, 'text/plain'),
	]
	start_response(status, response_headers)
	return iter([data])
