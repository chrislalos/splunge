class Response:
	def __init__ (self):
		self.status = (200, 'OK')
		self.headerMap = {}
		self.exc_info = None
		self.iter = None
	
	@property 
	def status (self): return '{} {}'.format(self.statusCode, self.statusMessage)
	@status.setter
	def status (self, value): (self.statusCode, self.statusMessage) = value

	@property
	def headers (self): return [(key, val) for key, val in self.headerMap.items()]

	def setHeader (self, name, value):
		self.headerMap

	def setHeaders (self, newHeaderMap):
		self.headerMap.clear()
		self.headerMap.update(newHeaderMap)

	def addLine (self, line='', *, encoding='latin-1'):
		if not self.iter:
			self.iter = []
		if isinstance(line, bytes):
			encodedLine = line
		elif isinstance(line, str):
			encodedLine = '{}\r'.format(line).encode(encoding)
		else:
			raise Exception('All lines must be strings or bytestrings')
		self.iter.append(encodedLine)


	def addLines (self, lines, *, encoding='latin-1'):
		for line in lines:
			self.addLine(line, encoding=encoding)


	def clearHeaders (self):
		self.headerMap.clear()



