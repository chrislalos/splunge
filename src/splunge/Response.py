from http.cookies import SimpleCookie
from . import Headers
from . import util
class Response:

	def __init__ (self):
		(self.statusCode, self.statusMessage) = (200, 'OK')
		self.headers = Headers()
		self.exc_info = None
		self.iter = []

	
	@property 
	def status (self): return '{} {}'.format(self.statusCode, self.statusMessage)


	def add_cookie (self, name, value, **kwargs): 
		headerName = 'Set-Cookie'
		headerValue = util.create_cookie_value(name, value, **kwargs) 
		self.headers.add(headerName, headerValue)

	def add_line (self, line, encoding='latin-1'):
		if not self.iter:
			self.iter = []
		encodedLine = '{}\r\n'.format(line).encode(encoding)
		self.iter.append(encodedLine)


	def add_lines (self, lines, *, encoding='latin-1'):
		for line in lines:
			self.addLine(line, encoding=encoding)
	
	
	def redirect (self, url):
		self.statusCode = 303
		self.statusMessage = f'Redirecting to {url}'
		self.headers.add('Location', url)
	# 
	#     def add (self, data):
	#         if not self.iter:
	#             self.iter = []
	#         if not isinstance(data, bytes):
	#             data = pickle.dumps(data)
	#         self.iter.append(data)
	# 		
	# 
	#     def addDownload (self, path, filename=None):
	#         with open(path, 'rb') as f:
	#             fData = f.read()
	#             if not filename:
	#                 (_, filename) = os.path.split(path)
	#                 mimeType = app.get_mime_type(path)
	#                 self.contentType = mimeType
	#                 self.contentLength = len(fData)
	#                 contentDisposition = "attachment: filename='{}'".format(filename)
	#                 self.headers.set('Content-Disposition', contentDisposition)
	#                 self.add(fData)
	# 
	# 
	#     def addLine (self, line, encoding='latin-1'):
	#         if not self.iter:
	#             self.iter = []
	#         encodedLine = '{}\r\n'.format(line).encode(encoding)
	#         self.iter.append(encodedLine)
	# 
	# 
	#     def addLines (self, lines, *, encoding='latin-1'):
	#         for line in lines:
	#             self.addLine(line, encoding=encoding)
	# 
	# 
	#     # def clearHeaders (self):
	#     #     self.headers.clear()
	# 
	# 
	#     # def deleteHeaders (self, name):
	#     #     self.headers.deleteAll(name)
	# 
	#     # def header (self, name):
	#     #     value = self.headers[name]
	#     #     if not value:
	#     #         return None
	#     #     if isinstance(value, list):
	#     #         raise Exception('Multiple values for {}'.format(name))
	#     #     return value
	# 
	# 	
	#     # def headers (self, name=None):
	#     #     if not name:
	#     #         return self.headers.asTuples()
	#     #     value = self.headers[name]
	#     #     if not value:
	#     #         return None
	#     #     if not isinstance(value, list):
	#     #         value = [value]
	#     #     return value
	# 
	# 
	#     def redirect (self, url):
	#         self.statusCode = 303
	#         self.statusMessage = 'Response Page to POST'
	#         self.setHeader('Location', url)
	# 
