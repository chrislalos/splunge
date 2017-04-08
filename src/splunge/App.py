# import urllib.parse

import errno
import imp
import inspect
import os
import os.path
from pprint import pprint
import sys
import traceback
import urllib.parse
import jinja2
from splunge import FaviconEx
from splunge import GeneralClientEx
from splunge import InvalidMethodEx
from splunge import ModuleNotFoundEx 
from splunge import MagicLoader
from splunge import PathString
from splunge import types
# from splunge import extracts


#######################################################################################
#
# To run splunge:
#
# cd yourWebAppFolder
# gunicorn -b localhost:portNumber splunge.App:Application (listen on a TCP socket)
#
#    or
#
# gunicorn -b unix:/tmp/splunge splunge.App:Application (listen on a Unix socket)
#
# In the likely event you run splunge behind nginx, use the Unix socket variant. 
# However the TCP socket method can be handy for quick testing
#
######################################################################################


def createAndEnhanceModule (moduleName, path):
	module = imp.load_source(moduleName, path)
	module.validateMethod = validateMethod
	return module


######################################################################################
#
# Splunge's enhanced exec module function.
#
# This function tries to do as little as possible, so it delegates the actual module
# execution to the modules own exec() method, as it should.
# 
# The only difference, is that this function captures the dir() of the module before
# and after. This lets the function detect which attributes have been added by module
# execution, which it assumes are of interest to the user. If no .pyp template file is
# defined, then the response body consists of name/value pairs of all these attributes.
#
def execModule (module):
	attrs1 = set(dir(module))
	module.exec()
	attrs2 = set(dir(module))
	newAttrs = [el for el in attrs2 if el not in attrs1 and el != '__builtins__']
	args = {'http': module.http}
	for attr in newAttrs:
		val = getattr(module, attr)
		# We don't want to include functions or classes
		if not callable(val): # and not inspect.isclass(val)
			args[attr] = getattr(module, attr)
	return args


# def inferTemplatePath (env):
# 	path = env['PATH_INFO']
# 	templateFilename = path[1:].partition('/')[0] + '.pyp'
# 	templatePath = os.path.join(os.getcwd(), templateFilename)
# 	return templatePath


# Shorthand for invoking jinja on a template string
def renderString (s, args):
	jenv = jinja2.Environment()
	jtemplate = jenv.from_string(s)
	s = jtemplate.render(args)
	return s


# Shorthand for invoking jinja on a template path
def renderTemplate (templatePath, args):
	jloader = jinja2.FileSystemLoader(os.getcwd())
	jenv = jinja2.Environment()
	templateName = os.path.basename(templatePath)
	jtemplate = jloader.load(jenv, templateName)
	if not args:
		args = {}
	s = jtemplate.render(args)
	return s 


def validateMethod (method, methods):
	if isinstance(methods, str):
		methods = [ methods ]
	if not method in [s.upper() for s in methods]:
		raise InvalidMethodEx(method, methods)


class Response:
	def __init__ (self):
		self.text = ''
		self.statusCode = 200
		self.statusMessage = 'OK'
		self.headers = []
	
	def addHeader (self, *args):
		headerTuple = argsToTuple(*args, length=2)
		self.headers.append(headerTuple)

	def getStatus (self):
		statusLine = '{} {}'.format(self.statusCode, self.statusMessage)
		return statusLine
	
	def handleError (self, statusCode, shortMsg, longMsg):
		self.setStatus(statusCode, shortMsg)
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

	def setContentType (self, contentType):
		self.addHeader('Content-type', contentType)

	def setStatus (self, statusCode, statusMessage):
		self.statusCode = statusCode
		self.statusMessage = statusMessage

	


###########################################################################################
#
# Here's what splunge does.
#
# For url http://yourhost/name
#
# Zeroth: Splunge checks to see if your file refers to static content (ie a simple text file,
#         html file, jpeg/png, etc). If so, it streams the contents back in the response, setting
#         Content-type appropriately.
#
# First: Splunge looks for a file named name.py
#        If name.py is found, splunge loads the module using magic loader, and executes it.
#        After executing the module, splunge checks if the special variable _ was set.
#        If _ was set and is of type bytes, _ is sent as the response body.
#        Otherwise _ is treated as a jinja template string and rendered using jinja
#        (This is a quick method for a user to write a single python file, which
#         does some processing and then returns a value)
#
#        After name.py is processed (if it existed), splunge looks for name.pyp
#        If name.pyp is found, splunge treats it as a jinja template and renders it.
#        If name.pyp is not found, splunge iterates over the module it just executed, and dumps 
#        all the variables that were set in the module.
#        (This is a quick method for a user to write a single pythong file, which does some
#         calculations, and then displays the results. What else would you want to do with a
#         python file in your webapp, with no associated template file?)
#        
#
#       Other than some error handling, that's splunge.
#
class Application ():
	def __init__ (self, env, start_response):
		self.env = env
		self.startResponse = start_response
		self.response = Response()
		self.path = self.env['PATH_INFO'].strip()
		print('path=' + self.path)
		try:
			self.handleRequest()
		except FileNotFoundError as ex:
			shortMsg = 'File Not Found'
			longMsg = "We're sorry, we were unable to find {}".format(self.path)
			self.handleError(404, shortMsg, longMsg)
		except GeneralClientEx as ex:
			shortMsg = 'General Client Error'
			longMsg = 'There was an error on the client side'
			self.handleError(400, shortMsg, longMsg)
		except InvalidMethodEx as ex:
			shortMsg = 'Method Not Allowed'
			allowHeaderValue = ex.getAllowHeaderValue()
			longMsg = 'Your HTTP request used an invalid method. Here is a list of allowed methods: {}'.format(allowHeaderValue)
			handleError(405, shortMsg, longMsg)
			self.response.addHeader('Allow', ex.getAllowHeaderValue())
		except jinja2.exceptions.TemplateNotFound as ex:
			shortMsg = 'Template file not found'
			longMsg = "We're sorry, we were unable to find {}".format(self.path)
			self.handleError(404, shortMsg, longMsg)
		except Exception as ex:
			shortMsg = 'General Server Error'
			longMsg = 'An error has occured on the server.'
			self.handleError(500, shortMsg, longMsg)
		else:
			# Check if content type header was explicitly set. If it was not then set it to text/html
			if not self.response.hasHeader('Content-Type'):
				self.response.addHeader('Content-Type', 'text/html')
		statusLine = self.response.getStatus()
		self.respond()



	def __iter__ (self):
		if isinstance(self.response.body, bytes):
			content = self.response.body
		else:
			content = self.response.body.encode('utf-8')
		yield content

	
	def createGetArgs (self):
		args = {}
		qs = self.env['QUERY_STRING']
		print('QUERY_STRING={}'.format(qs))
		d = urllib.parse.parse_qs(qs)
		pprint(d)
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


	def createHttpObject (self):
		http = type('', (), {})()                      # Creates an anonymous class and instantiates it
		http.env = self.env
		http.method = self.env['REQUEST_METHOD']
		http.path = PathString(self.env['PATH_INFO'])
		if http.method.lower() == 'get':
			http.args = self.createGetArgs()
		elif http.method.lower() == 'post':
			http.args = self.createPostArgs()
		else:
			http.args = {}
		return http


	######################################################################################
	#
	# This is the magic, which allows python modules in a splunge app to have 'global'
	# functions without doing any explicit imports. Who the heck wants to do imports?
	#
	# There is more value here than mere namespace pollution. E.g., instead of 
	# maintaining a response object, and having to call response.headers.append(), you 
	# can just call addHeader(). Nice.
	#
	def enrichModule (self, module):
		reqMethod = self.env['REQUEST_METHOD']
		module.http = self.createHttpObject()
		module.response = self.response
		module.addHeader =      lambda name, value: self.response.addHeader(name, value)
		module.validateMethod = lambda validMethods: validateMethod(reqMethod, validMethods)
		module.redirect =       lambda url: { self.response.redirect(url) }
		module.setContentType = lambda contentType: self.response.addHeader('Content-type', contentType)
		# import exceptions


	# Translate the path from the URL, to the local file or resource being referred to
	def getLocalPath (self):
		relPath = '{}{}'.format(os.getcwd(), self.path)
		return relPath		


	# Append .py to the path, then append the path to the working dir, and that's the python path
	def inferPythonPath (self):
		localPath = self.getLocalPath()
		pythonPath = '{}.py'.format(localPath)
		return pythonPath		


	# Get the local version of the http path, append .pyp, and that's the template path
	def inferTemplatePath (self):
		localPath = self.getLocalPath()
		templatePath = '{}.pyp'.format(localPath)
		return templatePath		


	def handleArgs (self, args):
		if '_' in args:
			self.handleShortcutResponse(args)
		else:
			self.handleTemplateFile(args)


	def handleError (self, statusCode, shortMsg, longMsg):
		traceback.print_exc()
		self.response.handleError(statusCode, shortMsg, longMsg)


	def handleRequest (self):
		if Application.isDefault(self.path):
			print('*** handleDefaultPath()')
			self.handleDefaultPath()
		elif Application.isFavicon(self.path):
			print('*** handleFavicon()')
			self.handleFavicon()
		elif self.isPythonFile():
			print('*** handlePythonFile()')
			localPath = self.getLocalPath()
			self.handlePythonFile(localPath)
		elif Application.isTemplateFile(self.path):
			print('*** handleTemplateFile()')
			localPath = self.getLocalPath()
			self.handleTemplateFile(localPath)
		elif self.isStaticContent():
			print('*** handleStaticContent()')
			self.handleStaticContent()
		else:
			pythonPath = self.inferPythonPath()
			if os.path.isfile(pythonPath):
				print('*** handlePythonFile()')
				self.handlePythonFile(pythonPath)
			else:
				templatePath = self.inferTemplatePath()
				if os.path.isfile(templatePath):
					print('*** handleTemplateFile()')
					self.handleTemplateFile(templatePath)
				else:
					localPath = self.getLocalPath()
					raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), localPath)


	def handleDefaultPath (self):
		self.response.body = ''
		print('Handling default path')
		self.setContentType('text/plain')
		self.addResponseLine('[splunge]')


	def handleFavicon (self):
		errmsg = 'The Favicon feature (favicon.ico) is not supported here, my friend'
		self.response.addHeader('Content-type', 'text/plain')
		self.response.addHeader('Warning', errmsg)
		self.response.statusCode = 410
		self.response.statusMessage = errmsg
		self.response.body = ''


	def handlePythonFile (self, path):
		self.response.body = ''
		module = MagicLoader.loadModule(path)
		print('module={}'.format(module))
		self.enrichModule(module)
		args = execModule(module)
		if '_' in args:
			print('Underscore detected - handling shortcut response')
			self.handleShortcutResponse(args)
		else:
			templatePath = self.inferTemplatePath()
			if os.path.isfile(templatePath):
				self.handleTemplateFile(templatePath, args)
			else:
  				print('template path was not found')
  				self.response.headers.append(('Content-Type', 'text/plain'))
  				for name in sorted(args):
  					value = args.get(name, '')
  					if not callable(value):
  						self.response.body += '{} = {}\n'.format(name, value)


	def handleShortcutResponse (self, args):
		underscore = args['_']
		if isinstance(underscore, bytes):
			self.response.body = underscore
		else:
			print('*** underscore')
			pprint(underscore)
			if not hasattr(underscore, '__dict__'):
				s = str(underscore)
				self.response.body = renderString(s, args)
			else:
				print('This is an object, so we are going to treat it like one')
				d = underscore.__dict__
				pprint(d)
				attrKeys = [key for key in d if not callable(d[key])]
				self.addResponseLine('<table>')
				for key in attrKeys:
					val = d[key]
					print('{}={}'.format(key, val))
					line = '<tr> <td>{}</td> <td>{}</td> </tr>'.format(key, val)
					self.addResponseLine(line)
				self.addResponseLine('</table>')


	def handleStaticContent (self):
		localPath = self.getLocalPath()
		print('localPath={}'.format(localPath))
		(root, ext) = os.path.splitext(localPath)
		defaultContentType = 'application/octet-stream'
		if not ext:
			contentType = defaultContentType
		else:			
			contentType = types.map.get(ext, defaultContentType)
		print('contentType={}'.format(contentType))
		self.setContentType(contentType)
		content = open(localPath, 'rb', buffering=0).readall()
		self.response.body = content


	def handleTemplateFile (self, path, args=None):
		print('templatePath={}'.format(path))
		print('About to execute template ...')
		if not args:
			args = {}
			args['http'] = self.createHttpObject()
		self.response.body = renderTemplate(path, args)


	def respond (self):
		status = self.response.getStatus()
		if hasattr(self.response, 'exc_info'):
			self.startResponse(status, self.response.headers, self.response.exc_info)
		else:
			self.startResponse(status, self.response.headers)


	@staticmethod
	def isDefault (path):
		flag = (path == '/')
		return flag



	@staticmethod
	def isFavicon (path):
		flag = (path.lower() == '/favicon.ico')
		return flag
		

	def isPythonFile (self):
		flag = (self.path.endswith('.py'))
		return flag


	def isStaticContent (self):
		localPath = self.getLocalPath()
		flag = os.path.isfile(localPath)
		return flag


	@staticmethod
	def isTemplateFile (path):
		flag = (path.endswith('.pyp'))
		return flag


	def getContentType (self):
		a = [v for (k,v) in self.response.headers if k.lower() == 'content-type']
		if a:
			contentType = a[0]
		else:
			contentType = None


	def setContentType (self, contentType):
		self.response.headers.append(('Content-Type', contentType))
	

	def addResponseLine (self, s):
		self.response.body += s
		self.response.body += '\r\n'



def argsToTuple (*args, length):
	print('*** args: {}'.format(args))
	print('len(args)={}'.format(len(args)))
	if len(args) == length:
		t = tuple(args)
	elif len(args) == 1 and isinstance(args[0], (list, tuple)) and len(args[0]) == length:
		t = tuple(args[0])
	else:
		raise Exception('Arguments must either be {} value(s) or a list or tuple {} element(s) long'.format(length, length))
	return t
