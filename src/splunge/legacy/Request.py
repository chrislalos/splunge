import os.path
import urllib.parse
from splunge import pathTests, PathString

class Request:
	def __init__ (self, env):
		self.env = env
	
	@property
	def args (self):
		return self.getArgs()

	# Translate the path from the URL, to the local file or resource being referred to
	@property 
	def localPath (self):
		relPath = os.path.join(os.getcwd(), self.path)
		return relPath		

	@property
	def method (self):
		return env['REQUEST_METHOD']


	@property
	def path (self):
		return PathString(self.env['PATH_INFO'].strip())

		
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
		if not 'CONTNT_LENGTH' in self.env:
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


	# Append .py to the path, then append the path to the working dir, and that's the python path
	def inferPythonPath (self):
		localPath = self.localPath
		pythonPath = '{}.py'.format(localPath)
		return pythonPath		

	
	# Get the local version of the http path, append .pyp, and that's the template path
	def inferTemplatePath (self):
		localPath = self.localPath
		templatePath = '{}.pyp'.format(localPath)
		return templatePath		

	
	def isDefault (self): return pathTests.isDefault(self.path)
	def isFavicon (self): return pathTests.isFavicon(self.path)
	def isPythonFile (self): return pathTests.isPythonFile(self.path)
	def isTemplateFile (self): return pathTests.isTemplateFile(self.path)

	def isStaticContent (self):
#		print("self.localPath={}".format(self.localPath))
		flag = os.path.isfile(self.localPath)
		return flag





