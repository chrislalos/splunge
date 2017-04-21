import sys
from splunge import util

class Response:
	def __init__ (self, start_response):
		self.body = None
		self.status = (200, 'OK')
		self.headers = []
		self.start_response = start_response
	
	
	@property 
	def status (self): return '{} {}'.format(self.statusCode, self.statusMessage)
	@status.setter
	def status (self, value): (self.statusCode, self.statusMessage) = value
	
	
	def addHeader (self, *args):
		headerTuple = util.argsToTuple(*args, length=2)
		self.headers.append(headerTuple)

	
	def addLine (self, s):
		self.body += s
		self.body += '\r\n'
	

	def getContentType (self):
		a = [v for (k,v) in self.headers if k.lower() == 'content-type']
		if a:
			contentType = a[0]
		else:
			contentType = None
		return contentType


	def handleError (self, statusCode, shortMsg, longMsg):
		self.status = (statusCode, shortMsg)
		self.setContentType('text/plain')
		self.addHeader('Warning', shortMsg)
		self.body = longMsg
		self.exc_info = sys.exc_info()

	def hasHeader (self, name):
		found = False
		name = name.lower()
		for (key, val) in self.headers:
			if key.lower() == name:
				found = True
				break
		return found

	def redirect (self, url):
		self.statusCode = 303
		self.statusMessage = 'Response Page to POST'
		self.addHeader('Location', url)

	
	def respond (self):
		if hasattr(self, 'exc_info'):
			self.start_response(self.status, self.headers, self.exc_info)
		else:
			self.start_response(self.status, self.headers)


	def setContentType (self, contentType):
		self.addHeader('Content-type', contentType)


	
	def setContentType (self, contentType):
		self.headers.append(('Content-Type', contentType))
