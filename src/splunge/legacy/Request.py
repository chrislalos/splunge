import urllib.parse
import os.path
from splunge import PathString

class Request:
	def __init__ (self, env):
		self.env = env
		self._args = self.getArgs()

	@property
	def args (self): return self._args
	@args.setter
	def args (self, value): self._args = value
	@property
	def localPath (self): return '{}{}'.format(os.getcwd(), self.path)
	@property
	def method (self): return self.env['REQUEST_METHOD']
	@property
	def path (self): return PathString(self.env['PATH_INFO'].strip())
	
	def createGetArgs (self):
		args = {}
		qs = self.env['QUERY_STRING']
#		print('QUERY_STRING={}'.format(qs))
		d = urllib.parse.parse_qs(qs)
#		pprint(d)
		for key, v in d.items():
			if v:
				if len(v) == 1:
					value = v[0]
				else:
					value = v
				args[key] = value
		return args
					

	# http://wsgi.tutorial.codepoint.net/parsing-the-request-post
	def createPostArgs (self):
		if not 'CONTENT_LENGTH' in self.env:
			contentLength = 0
		else:
			contentLength = int(self.env.get('CONTENT_LENGTH'))
		f = self.env['wsgi.input']
		qs = f.read(contentLength)
		args = urllib.parse.parse_qs(qs)
		postData = {}
		for key, val in args.items():
			postKey = key.decode()
			if len(val) == 1:
				postVal = val[0].decode()
			else:
				postVal = [el.decode() for el in val]
			postData[postKey] = postVal
		return postData


	def getArgs (self):
		if self.method.lower() == 'get':
			args = self.createGetArgs()
		elif self.method.lower() == 'post':
			args = self.createPostArgs()
		else: 
			args = {}
		return args

	def getPathExtension (self):
		(_, ext) = os.path.splitext(self.localPath)
		print("ext={}".format(ext))
		return ext
