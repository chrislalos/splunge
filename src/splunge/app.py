import copy
import os
import sys
from contextvars import ContextVar
from dataclasses import dataclass

import toml

from gunicorn.app.base import BaseApplication

from . import constants, handlers, loggin
from .Xgi import Xgi

handler_map = {
	"application/x-python-code": "SourceHandler",
	"application/x-splunge-template": "SourceHandler",
}

# Context variable for the current Xgi object
CV_xgi = ContextVar(constants.CTX_xgi)


# def create_handler(xgi: Xgi):
#	""" Return the appropriate handler for the wsgi. """
#	handler = None
#	if xgi.is_index_page():
#		handler =  IndexPageHandler()
#	elif xgi.is_python_module():
#		handler = PythonModuleHandler()
#	elif xgi.is_python_markup():
#		handler =  PythonTemplateHandler()
#	elif xgi.is_mime_type():
#		handler = create_mime_handler(xgi)
#	else:
#		handler = FileHandler()

#	if handler:
#		loggin.debug(f'handler found: {type(handler).__name__}')
#	else:
#		loggin.warning('no handler found')
#	return handler


class AppFactory(BaseApplication):
	def _init(self, cfg: "Config"):
	    self.cfg = cfg

	def load(self):
	    return wsgi_fn

	def load_config(self):
	    pass


@dataclass
class Config:
    contentFolders: list[str]
    codeFolders: list[str]
    guniCfg: dict
    logFolder: str
    name: str
    templateFolders: list[str]

    def __str__(self):
        import dataclasses
        d = {f.name: getattr(self, f.name) for f in dataclasses.fields(self)}
        return toml.dumps(d)

    def to_file(self, path):
        with open(path, 'w') as f:
            f.write(str(self))


@dataclass
class RunConfig:
    app: Config
    reload: bool = False
    debug: bool = False


def create_run_config(app, *, bind=None, codeFolders=None, contentFolders=None,
                      templateFolders=None, logFolder=None,
                      accessLog=None, errorLog=None,
                      reload=False, debug=False):
    app = copy.deepcopy(app)

    if bind is not None:
        app.guniCfg['bind'] = bind
    if codeFolders is not None:
        app.codeFolders = codeFolders
    if contentFolders is not None:
        app.contentFolders = contentFolders
    if templateFolders is not None:
        app.templateFolders = templateFolders
    if logFolder is not None:
        app.logFolder = logFolder

    if accessLog is not None:
        app.guniCfg['accesslog'] = accessLog
    elif 'accesslog' not in app.guniCfg:
        app.guniCfg['accesslog'] = os.path.join(app.logFolder, 'access.log')
    if errorLog is not None:
        app.guniCfg['errorlog'] = errorLog
    elif 'errorlog' not in app.guniCfg:
        app.guniCfg['errorlog'] = os.path.join(app.logFolder, 'error.log')

    if reload:
        app.guniCfg['reload'] = True

    os.makedirs(app.logFolder, exist_ok=True)
    os.makedirs(os.path.dirname(app.guniCfg['accesslog']), exist_ok=True)
    os.makedirs(os.path.dirname(app.guniCfg['errorlog']), exist_ok=True)

    return RunConfig(app=app, reload=reload, debug=debug)


@dataclass
class Context:
	cfg: Config
	xgi: Xgi


# def app(wsgi, start_response):
#	xgi = None
#	resp = None
#	try:
#		xgi = Xgi(wsgi)
#		loggin.debug(f"PATH_INFO={xgi['PATH_INFO']}")
#		loggin.debug(f"SCRIPT_NAME={xgi['SCRIPT_NAME']}")
#		loggin.debug(f"xwsgi.file_wrapper={getattr(xgi, 'file_wrapper', 'N/A')}")
#		handler = handlers.create(xgi)
#		resp = handler.handle_request()
#		status = resp.status
#		headers = resp.headers.asTuples()
#		data = resp.iter
#		start_response(status, headers)
#		# loggin.debug(f"len(data)={len(data)}")
#		# loggin.debug(f"len(data[0])={len(data[0])}")
#		return data
#	except FileNotFoundError as ex:
#		loggin.error(f"404 - {wsgi['PATH_INFO']}")
#		loggin.error(ex, exc_info=True)
#		return handlers.handle_404(xgi, start_response)
#	except Exception as ex:
#		loggin.warning('error caught in app()')
#		return handlers.handle_error(ex, wsgi, start_response)

# # error
# data = b'no clue dude'
# status = '513 no clue dude'
# response_headers = [
#	(Headers.HN_ContentLength, str(len(data))),
#	(Headers.HN_ContentType, 'text/plain'),
# ]
# start_response(status, response_headers)
# return iter([data])


# delegate legacy calls to the new function
def app(wsgi, start_response):
	return wsgi_fn(wsgi, start_response)


def createGunicornConfig(*, accessLog=None, bind=None, errorLog=None):
    d = {}
    if accessLog is not None:
        d["accesslog"] = accessLog
    if bind is not None:
        d["bind"] = bind
    if errorLog is not None:
        d["errorlog"] = errorLog
    return d


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
		return handlers.handle_404(xgi, start_response)
	except Exception as ex:
		loggin.exception("error caught in app()")
		return handlers.handle_error(ex, wsgi, start_response)

	# # error
	# data = b'no clue dude'
	# status = '513 no clue dude'
	# response_headers = [
	#	(Headers.HN_ContentLength, str(len(data))),
	#	(Headers.HN_ContentType, 'text/plain'),
	# ]
	# start_response(status, response_headers)
	# return iter([data])
