import os.path
import pickle
from . import util
from .Headers import Headers

class Response:
	def __init__ (self):
		self.status = (200, 'OK')
		self._headers = Headers()
		self.exc_info = None
		self.iter = None
	
	@property
	def contentLength (self): return self._headers.contentLength
	@contentLength.setter
	def contentLength (self, value): self._headers.contentLength = value

	@property
	def contentType (self): return self._headers.contentType
	@contentType.setter
	def contentType (self, value): self._headers.contentType = value

	@property 
	def status (self): return '{} {}'.format(self.statusCode, self.statusMessage)
	@status.setter
	def status (self, value): (self.statusCode, self.statusMessage) = value

#	@property
#	def headers (self): return [(key, val) for key, val in self.headerMap.items()]

	def setHeader (self, name, value):
		self.headerMap[name] = value

	def setHeaders (self, newHeaderMap):
		self.headerMap.clear()
		self.headerMap.update(newHeaderMap)

	def addHeader (self, name, value):
		self._headers.add(name, value)
		
	def hasHeader (self, name):
		return name in self._headers

	def setHeader (self, name, value):
		self._headers.set(name, value)


	def add (self, data):
		if not self.iter:
			self.iter = []
		if not isinstance(data, bytes):
			data = pickle.dumps(data)
		self.iter.append(data)
		

	def addDownload (self, path, filename=None):
		with open(path, 'rb') as f:
			fData = f.read()
		if not filename:
			(_, filename) = os.path.split(path)
		mimeType = util.getMimeType(path)
		self.contentType = mimeType
		self.contentLength = len(fData)
		contentDisposition = "attachment: filename='{}'".format(filename)
		self._headers.set('Content-Disposition', contentDisposition)
		self.add(fData)



	def addLine (self, line, encoding='latin-1'):
		if not self.iter:
			self.iter = []
		encodedLine = '{}\r\n'.format(line).encode(encoding)
		self.iter.append(encodedLine)


	def addLines (self, lines, *, encoding='latin-1'):
		for line in lines:
			self.addLine(line, encoding=encoding)


	def clearHeaders (self):
		self._headers.clear()


	def header (self, name):
		value = self._headers[name]
		if not value:
			return None
		if isinstance(value, list):
			raise Exception('Multiple values for {}'.format(name))
		return value

	
	def headers (self, name=None):
		if not name:
			return self._headers.asTuples()
		value = self._headers[name]
		if not value:
			return None
		if not isinstance(value, list):
			value = [value]
		return value


	def redirect (self, url):
		self.statusCode = 303
		self.statusMessage = 'Response Page to POST'
		self.setHeader('Location', url)


	def setContentType (self, contentType):
		self.setHeader('Content-type', contentType)
