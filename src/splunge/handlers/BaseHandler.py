from abc import ABC, abstractmethod
from .. import loggin, Xgi
from .. import handlers, Response

class BaseHandler(ABC):
	def __init__(self, xgi: Xgi):
		self.xgi = xgi

	# @classmethod
	# def create(xgi: Xgi):
	# 	""" Return the appropriate handler for the wsgi. """
	# 	handler = None
	# 	if xgi.is_index_page():
	# 		handler =  IndexPageHandler(xgi)
	# 	elif xgi.is_python_module():
	# 		handler = PythonModuleHandler(xgi)
	# 	elif xgi.is_python_markup():
	# 		handler =  PythonTemplateHandler(xgi)
	# 	elif xgi.is_mime_type():
	# 		handler = create_mime_handler(xgi)
	# 	else:
	# 		handler = FileHandler(xgi)
	# 	if handler:
	# 		loggin.debug(f'handler found: {type(handler).__name__}')
	# 	else:
	# 		loggin.warning('no handler found')
	# 	return handler

	@abstractmethod
	def handle_request(self, context: dict) -> Response:
		pass