from .Headers import Headers
from . import util
from . import loggin

def create_enrichment_object (xgi):
	""" Return an http enrichment object. """
	http = HttpEnricher(xgi)
	return http

def enrich_module(module, xgi):
	""" Enrich a module with a number of helper functions. """
	http = create_enrichment_object(xgi)
	setattr(module, 'http', http)
	return module


class HttpEnricher:
	statusCode: int = 200
	statusMessage: str = "OK"
	
	def __init__(self, xgi):
		self.xgi = xgi
		self.headers = Headers()
		
	@property
	def args(self):
		return self.xgi.create_args()
	@property
	def method(self): return self.xgi['REQUEST_METHOD']
	@property
	def path(self): return self.xgi['PATH_INFO']

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
		for key, value in sorted(self.xgi.items()):
			print('{}={}'.format(key, value))
		return None
	
	def redirect (self, url):
		loggin.debug(f"redirecting to {url}")
		self.statusCode = 303
		self.statusMessage = f'Redirecting to {url}'
		self.headers.add('Location', url)

	def validate_method(self, method, methods):
		return util.validate_method(method, methods)
