from .FileHandler import FileHandler
from .HtmlGenHandler import HtmlGenHandler
from .IndexPageHandler import IndexPageHandler
from .MarkdownHandler import MarkdownHandler
from .PythonModuleHandler import PythonModuleHandler
from .PythonTemplateHandler import PythonTemplateHandler
from .SourceHandler import SourceHandler
from ..Xgi import Xgi
from .. import loggin

lookupTable = {
	".html": ("text/html", FileHandler),
    ".md": ("text/markdown", MarkdownHandler),
	".png": ("image/png", FileHandler),
	".py": ("application/x-python-code", SourceHandler),
	".pyp": ("application/x-splunge-template", SourceHandler)
}

def create(xgi: Xgi):
	""" Return the appropriate handler for the wsgi. """
	handler = None
	if xgi.is_index_page():
		handler =  IndexPageHandler(xgi)
	elif xgi.is_python_module():
		handler = PythonModuleHandler(xgi)
	elif xgi.is_python_markup():
		handler =  PythonTemplateHandler(xgi)
	elif is_mime_type(xgi):
		handler = create_mime_handler(xgi)
	else:
		handler = FileHandler(xgi)
	if handler:
		loggin.debug(f'handler found: {type(handler).__name__}')
	else:
		loggin.warning('no handler found')
	return handler


def create_mime_handler(xgi):
	""" Return the appropriate MIME handler for the xgi. """
	# Get MIME type from path extension
	ext  = xgi.get_path_extension()
	if not ext in lookupTable:
		return None
	(_, handlerType) = lookupTable[ext]
	handler = handlerType(xgi)
	return handler

	
def is_mime_type(xgi):
	''' Check if the wsgi has a recognized MIME type. '''
	mimeType = lookup_mime_type(xgi)
	return not not mimeType 


def lookup_mime_type(xgi) -> str:
	''' Check if the wsgi has a recognized MIME type. '''
	ext = xgi.get_path_extension()
	loggin.debug(f'ext={ext}')
	if not ext in lookupTable:
		loggin.debug("ext not found in lookup table")
		return None
	(mimeType, _) = lookupTable[ext]
	loggin.debug(f'mimeType={mimeType}')
	return mimeType
	
