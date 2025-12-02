from .Response import Response
from . import util

def create_enrichment_object (wsgi):
	""" Return an http enrichment object. """
	http = HttpEnricher(wsgi)
	return http

def enrich_module(module, wsgi):
	""" Enrich a module with a number of helper functions. """
	http = create_enrichment_object(wsgi)
	setattr(module, 'http', http)
	return module


class HttpEnricher:
	def __init__(self, wsgi):
		self.wsgi = wsgi
		self.resp = Response()
		self.method = wsgi['REQUEST_METHOD']
		self.path = wsgi['PATH_INFO']
		self.args = util.create_wsgi_args(wsgi)

	def add_cookie (self, name, value, **kwargs): 
		self.resp.add_cookie(name, value, kwargs)
	
	def pypinfo (self):
		for key, value in sorted(self.wsgi.items()):
			print('{}={}'.format(key, value))
		return None
	
	def set_content_length(self, contentLength):
		self.resp.headers.add('Content-Length', contentLength)

	def set_content_type(self, contentType):
		self.resp.contentType = contentType

	def validate_method(self, method, methods):
		return util.validate_method(method, methods)
