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
		self.text = ""
		self.headers = []


###########################################################################################
#
# Here's what splunge does.
#
# For url http://yourhost/name
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
		print("path=" + self.path)
		try:
			self.handleRequest()
		except FaviconEx as ex:
			print(ex)
			errmsg = "The Favicon feature (favicon.ico) is not supported here, my friend"
			headers = [
				('Content-type', 'text/plain'),
				('Warning', errmsg)
			]
			self.startResponse("410 {}".format(errmsg), headers, sys.exc_info())
			self.response.body = errmsg
		except FileNotFoundError as ex:
			print(ex)
			headers = [
				('Content-type', 'text/plain'),
			]
			self.startResponse('404 File Not Found', headers, sys.exc_info())
			self.response.body = str(ex)
		except GeneralClientEx as ex:
			print(ex)
			headers = [
				('Content-type', 'text/plain'),
				('Warning', ex.getWarningHeaderValue())
			]
			self.startResponse('400 Oops', headers, sys.exc_info())
			self.response.body = str(ex)
		except InvalidMethodEx as ex:
			print(ex)
			headers = [
				("Content-type", "text/plain"),
				("Allow", ex.getAllowHeaderValue())
			]
			self.startResponse("405", headers, sys.exc_info())
			self.response.body = str(ex)
		except jinja2.exceptions.TemplateNotFound as ex:
			msg = "Template file not found: {}".format(ex.message)
			headers = [
				("Content-type", "text/plain"),
				("Warning", msg)
			]
			self.startResponse("404", headers, sys.exc_info())
			self.response.body = msg 
		except Exception as ex:
			traceback.print_exc()
			headers = [
				("Content-type", "text/plain")
			]
			self.startResponse("500", headers, sys.exc_info())
			self.response.body = "An error has occured on the server."
		else:
			# Check if content type header was explicitly set. If it was not then set it to text/html
			for (key, val) in self.response.headers:
				if key.lower() == 'content-type':
					break
			else:
				self.response.headers.append(('Content-Type', 'text/html'))
			self.startResponse('200 OK', self.response.headers)


	def __iter__ (self):
		if isinstance(self.response.body, bytes):
			content = self.response.body
		else:
			content = self.response.body.encode('utf-8')
		yield content

	
	def createGetArgs (self):
		args = {}
		qs = self.env['QUERY_STRING']
		print("QUERY_STRING={}".format(qs))
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
					


	def createPostArgs (self):
		args = {}


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
	# Note there is more value here than mere namespace pollution. E.g., instead of 
	# maintaining a response object, and having to call response.headers.append(), you 
	# can just call addHeader(). Nice.
	#
	def enrichModule (self, module):
		reqMethod = self.env['REQUEST_METHOD']
		# Assigning a null lambda is apparently an acceptable Python idiom for creating an anonymous object
		module.http = self.createHttpObject()
		module.response = self.response
		module.addHeader = lambda x, y: self.response.headers.append((x, y))
		module.validateMethod = lambda x: validateMethod(reqMethod, x) 
		module.setContentType = lambda x: self.response.headers.append(('Content-type', x))
		# import exceptions


	# Translate the path from the URL, to the local file or resource being referred to
	def getLocalPath (self):
		relPath = "{}{}".format(os.getcwd(), self.path)
		return relPath		


	# Append .py to the path, then append the path to the working dir, and that's the python path
	def inferPythonPath (self):
		localPath = self.getLocalPath()
		pythonPath = "{}.py".format(localPath)
		return pythonPath		


	# Get the local version of the http path, append .pyp, and that's the template path
	def inferTemplatePath (self):
		localPath = self.getLocalPath()
		templatePath = "{}.pyp".format(localPath)
		return templatePath		


	def handleArgs (self, args):
		if '_' in args:
			self.handleShortcutResponse(args)
		else:
			self.handleTemplateFile(args)
#  			print("template path was not found")
#  			self.response.headers.append(('Content-Type', 'text/plain'))
#  			for name in sorted(self.args):
#  				value = self.args.get(name, '')
#  				if not callable(value):
#  					self.response.text += "{} = {}\n".format(name, value)


	def handleRequest (self):
		if Application.isDefault(self.path):
			print("*** handleDefaultPath()")
			self.handleDefaultPath()
		elif Application.isFavicon(self.path):
			print("*** handleFavicon()")
			self.handleFavicon()
		elif self.isPythonFile():
			print("*** handlePythonFile()")
			localPath = self.getLocalPath()
			self.handlePythonFile(localPath)
		elif Application.isTemplateFile(self.path):
			print("*** handleTemplateFile()")
			localPath = self.getLocalPath()
			self.handleTemplateFile(localPath)
		elif self.isStaticContent():
			print("*** handleStaticContent()")
			self.handleStaticContent()
		else:
			pythonPath = self.inferPythonPath()
			if os.path.isfile(pythonPath):
				print("*** handlePythonFile()")
				self.handlePythonFile(pythonPath)
			else:
				templatePath = self.inferTemplatePath()
				if os.path.isfile(templatePath):
					print("*** handleTemplateFile()")
					self.handleTemplateFile(templatePath)
				else:
					localPath = self.getLocalPath()
					raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), localPath)


	def handleDefaultPath (self):
		self.response.body = ""
		print("Handling default path")
		self.setContentType('text/plain')
		self.addResponseLine("[splunge]")


	def handleFavicon (self):
		raise FaviconEx()


	def handlePythonFile (self, path):
		self.response.body = ""
		module = MagicLoader.loadModule(path)
		print("module={}".format(module))
		self.enrichModule(module)
		args = execModule(module)
		if '_' in args:
			print("Underscore detected - handling shortcut response")
			self.handleShortcutResponse(args)
		else:
			templatePath = self.inferTemplatePath()
			if os.path.isfile(templatePath):
				self.handleTemplateFile(templatePath, args)
			else:
  				print("template path was not found")
  				self.response.headers.append(('Content-Type', 'text/plain'))
  				for name in sorted(args):
  					value = args.get(name, '')
  					if not callable(value):
  						self.response.body += "{} = {}\n".format(name, value)


	def handleShortcutResponse (self, args):
		underscore = args['_']
		if isinstance(underscore, bytes):
			self.response.body = underscore
		else:
			print('*** underscore')
			pprint(underscore)
			if not hasattr(underscore, '__dict__'):
				self.response.body = renderString(underscore, args)
			else:
				print("This is an object, so we are going to treat it like one")
				d = underscore.__dict__
				pprint(d)
				attrKeys = [key for key in d if not callable(d[key])]
				self.addResponseLine("<table>")
				for key in attrKeys:
					val = d[key]
					print("{}={}".format(key, val))
					line = "<tr> <td>{}</td> <td>{}</td> </tr>".format(key, val)
					self.addResponseLine(line)
				self.addResponseLine("</table>")


	def handleStaticContent (self):
		localPath = self.getLocalPath()
		print("localPath={}".format(localPath))
		(root, ext) = os.path.splitext(localPath)
		defaultContentType = "application/octet-stream"
		if not ext:
			contentType = defaultContentType
		else:			
			contentType = types.map.get(ext, defaultContentType)
		print("contentType={}".format(contentType))
		self.setContentType(contentType)
		content = open(localPath, 'rb', buffering=0).readall()
		self.response.body = content


	def handleTemplateFile (self, path, args=None):
		print("templatePath={}".format(path))
		print("About to execute template ...")
		if not args:
			args = {}
			args['http'] = self.createHttpObject()
		self.response.body = renderTemplate(path, args)


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
		self.response.body += "\r\n"


