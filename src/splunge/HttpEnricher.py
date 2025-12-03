from .Headers import Headers
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
	statusCode: int = 200
	statusMessage: str = "OK"
	
	def __init__(self, wsgi):
		self.wsgi = wsgi
		self.headers = Headers()
		
	@property
	def args(self): return util.create_wsgi_args(self.wsgi)
	@property
	def method(self): return self.wsgi['REQUEST_METHOD']
	@property
	def path(self): return self.wsgi['PATH_INFO']

	# Content-Length
	@property
	def contentLength(self): return self.headers.contentLength
	@contentLength.setter
	def contentLength(self, val): self.headers.contentLength = val
	
	# Content-Type
	@property
	def contentType(self): return self.headers.contentType
	@contentType.setter
	def contentType(self, val): self.headers.contentType = val
	
	# Location
	@property
	def location(self): return self.headers.location
	@location.setter
	def location(self, val): self.headers.location = val
	
	# Status
	@property
	def status(self): return f"{self.statusCode} {self.statusMessage}"
	@status.setter
	def status(self, val: str):
		sStatusCode, _, self.statusMessage = val.partition(' ')
		self.statusCode = int(sStatusCode)
	
	
	def add_cookie (self, name, value, **kwargs): 
		self.resp.add_cookie(name, value, kwargs)
	
	
	def pypinfo (self):
		for key, value in sorted(self.wsgi.items()):
			print('{}={}'.format(key, value))
		return None
	
	def redirect (self, url):
		self.statusCode = 303
		self.statusMessage = f'Redirecting to {url}'
		self.headers.add('Location', url)

	def validate_method(self, method, methods):
		return util.validate_method(method, methods)
