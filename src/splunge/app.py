import contextlib
import html
from http.cookies import SimpleCookie
import importlib
import inspect
import io
import os
import pathlib
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
from .Xgi import Xgi


handler_map = {'application/x-python-code': "SourceHandler",
               'application/x-splunge-template': "SourceHandler"
              }


def create_handler(xgi: Xgi):
	""" Return the appropriate handler for the wsgi. """
	handler = None
	if xgi.is_index_page():
		handler =  IndexPageHandler()
	elif xgi.is_python_module():
		handler = PythonModuleHandler()
	elif xgi.is_python_markup():
		handler =  PythonTemplateHandler()
	elif xgi.is_mime_type():
		handler = create_mime_handler(xgi)
	else:
		handler = FileHandler()
	
	if handler:
		loggin.debug(f'handler found: {type(handler).__name__}')
	else:
		loggin.warning('no handler found')
	return handler


def handle_404(xgi, start_response):
	loggin.debug("inside handle_404()")
	status = "404 Resource Not Found"
	templatePath = os.path.abspath(f'{os.getcwd()}/err/404.pyp')
	loggin.debug(f'templatePath={templatePath}')
	# Load the template & render it w wsgi args
	if not os.path.exists(templatePath):
		raise Exception(f'template path not found: {templatePath}')
	args = {"path": xgi['PATH_INFO']}
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


def handle_error(ex, xgi, start_response):
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
	xgi = Xgi(wsgi)
	resp = None
	try:
		loggin.debug(f"PATH_INFO={xgi['PATH_INFO']}")
		loggin.debug(f"SCRIPT_NAME={xgi['SCRIPT_NAME']}")
		loggin.debug(f"xwsgi.file_wrapper={getattr(xgi, 'file_wrapper', 'N/A')}")
		handler = create_handler(xgi)
		respData = handler.handle_request(xgi)
		loggin.debug(f'respData={respData}')
		(resp, done) = respData
	except FileNotFoundError as ex:
		loggin.error(f"404 - {wsgi['PATH_INFO']}")
		loggin.error(ex, exc_info=True)
		return handle_404(xgi, start_response)
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
