import html
import os
import traceback

from . import error_template_strings, loggin, util
from . import handlers
from .Headers import Headers
from .Xgi import Xgi


handler_map = {'application/x-python-code': "SourceHandler",
			   'application/x-splunge-template': "SourceHandler"
			  }


# def create_handler(xgi: Xgi):
# 	""" Return the appropriate handler for the wsgi. """
# 	handler = None
# 	if xgi.is_index_page():
# 		handler =  IndexPageHandler()
# 	elif xgi.is_python_module():
# 		handler = PythonModuleHandler()
# 	elif xgi.is_python_markup():
# 		handler =  PythonTemplateHandler()
# 	elif xgi.is_mime_type():
# 		handler = create_mime_handler(xgi)
# 	else:
# 		handler = FileHandler()
	
# 	if handler:
# 		loggin.debug(f'handler found: {type(handler).__name__}')
# 	else:
# 		loggin.warning('no handler found')
# 	return handler


def handle_404(xgi, start_response):
	status = "404 Resource Not Found"
	try:
		loggin.debug("inside handle_404()")
		templatePath = f'/err/404.pyp'
		loggin.debug(f'templatePath={templatePath}')
		# Load the template & render it w wsgi args
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
	except Exception as ex:
		loggin.error(ex)
		content = util.render_string(error_template_strings.Err404, args).encode('utf-8')
		contentLength = len(content)
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = "text/html"
		start_response(status, headers.asTuples())
		return [content]


def handle_error(ex, xgi, start_response):
	status = "513 uhoh"
	try:
		loggin.error(ex, exc_info=True)
		# Create a traceback from the ex + create a context from the message+traceback
		ss = traceback.extract_tb(ex.__traceback__)
		s = "".join([html.escape(line).lstrip() for line in ss.format()])
		args = {
			"message": str(ex),
			"traceback": s
		}
		# Load + render the template, and encode as HTML
		templatePath = '/err/500.pyp'
		content = util.render_template(templatePath, args).encode('utf-8')
		# Create headers
		contentLength = len(content)
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = "text/html"
		# Deliver the response
		start_response(status, headers.asTuples())
		return [content]
	except Exception as ex:
		loggin.error(ex, exc_info=True)
		content = util.render_string(error_template_strings.Err500, args).encode('utf-8')
		contentLength = len(content)
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = "text/html"
		start_response(status, headers.asTuples())
		return [content]


def app(wsgi, start_response):
	xgi = None
	resp = None
	try:
		xgi = Xgi(wsgi)
		loggin.debug(f"PATH_INFO={xgi['PATH_INFO']}")
		loggin.debug(f"SCRIPT_NAME={xgi['SCRIPT_NAME']}")
		loggin.debug(f"xwsgi.file_wrapper={getattr(xgi, 'file_wrapper', 'N/A')}")
		handler = handlers.create(xgi)
		resp = handler.handle_request()
		status = resp.status
		headers = resp.headers.asTuples() 
		data = resp.iter
		start_response(status, headers)
		# loggin.debug(f"len(data)={len(data)}")
		# loggin.debug(f"len(data[0])={len(data[0])}")
		return data
	except FileNotFoundError as ex:
		loggin.error(f"404 - {wsgi['PATH_INFO']}")
		loggin.error(ex, exc_info=True)
		return handle_404(xgi, start_response)
	except Exception as ex:
		loggin.warning('error caught in app()')
		return handle_error(ex, wsgi, start_response)

	# # error
	# data = b'no clue dude'
	# status = '513 no clue dude'
	# response_headers = [
	# 	(Headers.HN_ContentLength, str(len(data))),
	# 	(Headers.HN_ContentType, 'text/plain'),
	# ]
	# start_response(status, response_headers)
	# return iter([data])



def app(wsgi, start_response):
	xgi = None
	resp = None
	try:
		xgi = Xgi(wsgi)
		loggin.debug(f"PATH_INFO={xgi['PATH_INFO']}")
		loggin.debug(f"SCRIPT_NAME={xgi['SCRIPT_NAME']}")
		loggin.debug(f"xwsgi.file_wrapper={getattr(xgi, 'file_wrapper', 'N/A')}")
		handler = handlers.create(xgi)
		resp = handler.handle_request()
		status = resp.status
		headers = resp.headers.asTuples() 
		data = resp.iter
		start_response(status, headers)
		# loggin.debug(f"len(data)={len(data)}")
		# loggin.debug(f"len(data[0])={len(data[0])}")
		return data
	except FileNotFoundError as ex:
		loggin.error(f"404 - {wsgi['PATH_INFO']}")
		loggin.error(ex, exc_info=True)
		return handle_404(xgi, start_response)
	except Exception as ex:
		loggin.warning('error caught in app()')
		return handle_error(ex, wsgi, start_response)

	# # error
	# data = b'no clue dude'
	# status = '513 no clue dude'
	# response_headers = [
	# 	(Headers.HN_ContentLength, str(len(data))),
	# 	(Headers.HN_ContentType, 'text/plain'),
	# ]
	# start_response(status, response_headers)
	# return iter([data])
