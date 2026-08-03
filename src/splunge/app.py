from contextvars import ContextVar
from dataclasses import dataclass
import html
import os
import traceback

from gunicorn.app.base import BaseApplication

from . import constants
from . import error_template_strings, loggin, util
from . import handlers
from .Headers import Headers
from .Xgi import Xgi


handler_map = {'application/x-python-code': "SourceHandler",
			   'application/x-splunge-template': "SourceHandler"
			  }

# Context variable for the current Xgi object
CV_xgi = ContextVar(constants.CTX_xgi)


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


class AppFactory(BaseApplication):
	def _init(self, cfg, guniCfg):
		self.cfg, guniCfg
		self.guniCfg = guniCfg

	def load(self):
		return wsgi_fn

	def load_config(self):
		pass

class Config:
    def __init__(self, *,
                 name,
                 bind,
                 contentFolders=[],
                 codeFolders=[],
                 templateFolders=[]):
        self.name = name
        self.contentFolders = contentFolders
        self.codeFolders = codeFolders
        self.templateFolders = templateFolders
        self.gunicornConfig = dict()


@dataclass
class Context:
	cfg: Config
	xgi: Xgi


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
		return handlers.handle_404(xgi, start_response)
	except Exception as ex:
		loggin.warning('error caught in app()')
		return handlers.handle_error(ex, wsgi, start_response)

	# # error
	# data = b'no clue dude'
	# status = '513 no clue dude'
	# response_headers = [
	# 	(Headers.HN_ContentLength, str(len(data))),
	# 	(Headers.HN_ContentType, 'text/plain'),
	# ]
	# start_response(status, response_headers)
	# return iter([data])


# delegate legacy calls to the new function
def app(wsgi, start_response):
    return wsgi_fun(wsgi, start_response)


def wsgi_fn(wsgi, start_response):
	xgi = None
	resp = None
	try:
		xgi = Xgi(wsgi)
		handler = handlers.create(xgi)
		resp = handler.handle_request()
		status = resp.status
		headers = resp.headers.asTuples() 
		data = resp.iter
		start_response(status, headers)
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
