# import urllib.parse

import imp
import inspect
import os.path
import sys
import traceback
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
# gunicorn -b localhost:somePortNumber splunge.App:Application (listen on a port)
#
#    or
#
# gunicorn -b unix:/tmp/splunge splunge.App:Application (listen on a Unix socket)
#
# In the likely event you run splunge behind nginx, use the Unix socket variant. 
# However the socket method can be handy for quick testing
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
		if not callable(val) and not inspect.isclass(val):
			args[attr] = getattr(module, attr)
	return args


def getTemplatePath (env):
	path = env['PATH_INFO']
	templateFilename = path[1:].partition('/')[0] + '.pyp'
	templatePath = os.path.join(os.getcwd(), templateFilename)
	return templatePath


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
		print("path=" + self.getPath())
		try:
			self.handleRequest()
			if self.args:
				self.handleArgs()
		except FaviconEx as ex:
			print(ex)
			errmsg = "The Favicon feature (favicon.ico) is not supported here, my friend"
			headers = [
				('Content-type', 'text/plain'),
				('Warning', errmsg)
			]
			self.startResponse("410 {}".format(errmsg), headers, sys.exc_info())
			self.response.text = errmsg
		except FileNotFoundError as ex:
			print(ex)
			headers = [
				('Content-type', 'text/plain'),
			]
			self.startResponse('404 File Not Found', headers, sys.exc_info())
			self.response.text = str(ex)
		except GeneralClientEx as ex:
			print(ex)
			headers = [
				('Content-type', 'text/plain'),
				('Warning', ex.getWarningHeaderValue())
			]
			self.startResponse('400 Oops', headers, sys.exc_info())
			self.response.text = str(ex)
		except InvalidMethodEx as ex:
			print(ex)
			headers = [
				("Content-type", "text/plain"),
				("Allow", ex.getAllowHeaderValue())
			]
			self.startResponse("405", headers, sys.exc_info())
			self.response.text = str(ex)
		except jinja2.exceptions.TemplateNotFound as ex:
			msg = "Template file not found: {}".format(ex.message)
			headers = [
				("Content-type", "text/plain"),
				("Warning", msg)
			]
			self.startResponse("404", headers, sys.exc_info())
			self.response.text = msg 
		except Exception as ex:
			traceback.print_exc()
			headers = [
				("Content-type", "text/plain")
			]
			self.startResponse("500", headers, sys.exc_info())
			self.response.text = "An error has occured on the server."
		else:
			# Check if content type header was explicitly set. If it was not then set it to text/html
			for (key, val) in self.response.headers:
				if key.lower() == 'content-type':
					break
			else:
				self.response.headers.append(('Content-Type', 'text/html'))
			self.startResponse('200 OK', self.response.headers)

		
	def __iter__ (self):
		print("__iter__ being called")
		if isinstance(self.response.text, bytes):
			content = self.response.text
		else:
			content = self.response.text.encode('utf-8')
		yield content

	
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
		module.http = lambda: None 
		module.http.env = self.env
		module.http.method = self.env['REQUEST_METHOD']
		module.http.path = PathString(self.env['PATH_INFO'])
		# module.http.pathParts = env['PATH_INFO'][1:].split('/')
		module.addHeader = lambda x, y: self.response.headers.append((x, y))
		module.validateMethod = lambda x: validateMethod(reqMethod, x) 
		module.setContentType = lambda x: self.response.headers.append(('Content-type', x))
		# import exceptions


	# Translate the path from the URL, to the local file or resource being referred to
	def getLocalPath (self):
		path = self.getPath()
		relPath = "{}{}".format(os.getcwd(), path)
		return relPath		


	def getModulePath (self):
		path = self.getPath()
		moduleFilename = path[1:].partition('/')[0] + '.py'
		modulePath = os.path.join(os.getcwd(), moduleFilename)
		return modulePath


	# Append .py to the path, then append the path to the working dir, and that's the python path
	def getPythonPath (self):
		localPath = self.getLocalPath()
		pythonPath = "{}.py".format(localPath)
		return pythonPath		


	# Append .pyp to the path, then append the path to the working dir, and that's the python path
	def getTemplatePath (self):
		localPath = self.getLocalPath()
		templatePath = "{}.pyp".format(localPath)
		return templatePath		


	def getPath (self):
		path = self.env['PATH_INFO'].strip()
		return path


	def handleArgs (self):
		if '_' in self.args:
			self.handleShortcutResponse()
		else:
			self.handleTemplateFile()
#  			print("template path was not found")
#  			self.response.headers.append(('Content-Type', 'text/plain'))
#  			for name in sorted(self.args):
#  				value = self.args.get(name, '')
#  				if not callable(value):
#  					self.response.text += "{} = {}\n".format(name, value)


	def handleRequest (self):
		if self.isDefault():
			self.handleDefaultPath()
		elif self.isFavicon():
			self.handleFavicon()
		elif self.isPythonFile():
			self.handlePythonFile()
		elif self.isTemplateFile():
			self.handleTemplateFile()
		else:
			self.handleStaticContent()


	def handleShortcutResponse (self):
		if isinstance(args['_'], bytes):
			self.response.text = args['_']
		else:
			self.response.text = renderString(str(args['_']), args)



	def handleDefaultPath (self):
		print("Handling default path")
		self.setContentType('text/plain')
		self.addResponseLine("/")
		self.args = None


	def handleFavicon (self):
		raise FaviconEx()


	def handlePythonFile (self):
		modulePath = self.getModulePath()
		print("modulePath=".format(modulePath))
		module = MagicLoader.loadModule(modulePath)
		print("module={}".format(module))
		self.enrichModule(module)
		self.args = execModule(module)


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
		self.response.text = content
		self.args = None


	def handleTemplateFile (self):
 		templatePath = self.getTemplatePath()
 		print("templatePath={}".format(templatePath))
 		print("templatePath=" + templatePath)
 		print("About to execute template ...")
 		self.response.text = renderTemplate(templatePath, self.args)


	def isDefault (self):
		flag = (self.getPath() == '/')
		return flag



	def isFavicon (self):
		print("*** in isFavicon(): self.getPath().lower() == {}".format(self.getPath().lower()))
		flag = (self.getPath().lower() == '/favicon.ico')
		return flag
		

	def isPythonFile (self):
		path = self.getPythonPath()
		print("pythonPath={}".format(path))
		flag = os.path.isfile(path)
		return flag


	def isTemplateFile (self):
		path = self.getTemplatePath()
		print("templatePath={}".format(path))
		flag = (self.getPath().endswith('.pyp'))
		return flag


	def setContentType (self, contentType):
		self.response.headers.append(('Content-Type', contentType))
	

	def addResponseLine (self, s):
		self.response.text += s
		self.response.text += "\r\n"


# 	def misc ():
# 		print("modulePath={}".format(modulePath))
# 		if not modulePath:
# 			print("modulePath didn't exist")
# 		try:
# 			handleModulePath(modulePath)
# 			module = MagicLoader.loadModule(modulePath)
# 			print("module={}".format(module))
# 			enrichModule(module, env, self)
# 			args = execModule(module)
# 		except ModuleNotFoundEx as ex:
# 			print('Module {} not found - skipping pre-processing'.format(ex.moduleName))
# 			args = {}
# 		if '_' in args:
# 			if isinstance(args['_'], bytes):
# 				self.response.text = args['_']
# 			else:
# 				self.response.text = renderString(str(args['_']), args)
# 		else:
# 			templatePath = getTemplatePath(env)
# 			print("templatePath={}".format(templatePath))
# 			if not os.path.isfile(templatePath):
# 				print("template path was not found")
# 				self.response.headers.append(('Content-Type', 'text/plain'))
# 				for name in sorted(args):
# 					value = args[name]
# 					# print("type({})={}".format(value, type(value)))
# 					if not callable(value):
# 						self.response.text += "{} = {}\n".format(name, value)
# 			else:
# 				print("templatePath=" + templatePath)
# 				print("About to execute template ...")
# 				self.response.text = renderTemplate(templatePath, args)


# 	def generatePage (self):
# 		path = self.env['PATH_INFO']
# 		parts = path.split('/')
# 		extractId = parts[2]
# 		datestr = parts[3]
# 		dtRange = DateRangeParser.getDateRange(datestr)
# 		(dtStart, dtEnd) = dtRange
# 		args = {
# 			'extractId': extractId,
# 			'dtStart': dtStart,
# 			'dtEnd': dtEnd
# 		}
# 
# 		jloader = jinja2.FileSystemLoader('/home/ubuntu/dev/py/splunge/templates')
# 		jenv = jinja2.Environment()
# 		jtemplate = jloader.load(jenv, 'extracts.pyp')
# 		self.response.text = jtemplate.render(args)
# 
# 	def dumpParts (self):
# 		for i, part in enumerate(parts):
# 			self.response.text += "{} => {}<br>".format(i, part)
# 
# 	def validateParts (self):
# 		path = self.env['PATH_INFO']
# 		parts = path.split('/')
# 		if len(parts) < 4 or len(parts[0]) > 0 or not DateRangeParser.isValid(parts[3]):
# 			msg = "URL path must be of form /extract/[extractId]/YYMMDD or /extract/[extractId]/YYMMDD-YYMMDD"
# 			raise GeneralClientEx(msg)

# 			path = env['PATH_INFO']
# 			parts = path.split('/')
# 			moduleStub = parts[1]	
# #			moduleName = 'splunge.{}'.format(moduleStub)
# #			modulePath = 'splunge/{}.py'.format(moduleStub)
# #			module = createAndEnhanceModule(moduleName, modulePath)
# 			filename = '{}.py'.format(moduleStub)
# 			args = {}
# 			g = {}
# 			g['validateMethod'] = validateMethod
# 			g['app'] = self 
# 			g['args'] = args
# 			with open(filename) as f:
# 				code = compile(f.read(), filename, 'exec')
# 				exec(code, g)
# #			module.validateMethod = validateMethod
# #			module.app = self
# #			args = []
# #			module.args = args
# #			validate = getattr(module, 'validate')
# #			generatePage = getattr(module, 'generatePage')
# #			validate(self)
# 			self.startResponse('200 OK', [('Content-type', 'text/html')])
# 			jloader = jinja2.FileSystemLoader('/home/ubuntu/dev/py/splunge/templates')
# 			jenv = jinja2.Environment()
# 			jtemplate = jloader.load(jenv, 'extracts.pyp')
# 			self.response.text = jtemplate.render(args)
#			modulePath = self.getModulePath()
#			print("modulePath={}".format(modulePath))
#			if not modulePath:
#				print("modulePath didn't exist")
#			try:
#				handleModulePath(modulePath)
#				module = MagicLoader.loadModule(modulePath)
#				print("module={}".format(module))
#				enrichModule(module, env, self)
#				args = execModule(module)
#			except ModuleNotFoundEx as ex:
#				print('Module {} not found - skipping pre-processing'.format(ex.moduleName))
#				args = {}
#			if '_' in args:
#				if isinstance(args['_'], bytes):
#					self.response.text = args['_']
#				else:
#					self.response.text = renderString(str(args['_']), args)
# 			else:
# 				templatePath = getTemplatePath(env)
# 				print("templatePath={}".format(templatePath))
# 				if not os.path.isfile(templatePath):
# 					print("template path was not found")
# 					self.response.headers.append(('Content-Type', 'text/plain'))
# 					for name in sorted(args):
# 						value = args[name]
# 						# print("type({})={}".format(value, type(value)))
# 						if not callable(value):
# 							self.response.text += "{} = {}\n".format(name, value)
# 				else:
# 					print("templatePath=" + templatePath)
# 					print("About to execute template ...")
# 					self.response.text = renderTemplate(templatePath, args)

#	extractId = parts[2]
#	datestr = parts[3]
	
#	try:
#		utils.validateRequestMethod(env, ['GET'])
#		dtRange = dateRangeParser.getDateRange(datestr)
#		(dtStart, dtEnd) = dtRange
#		resp += "<table>"
#		resp += "<tr> <td>extractId</td> <td>{}</td> </tr>".format(extractId)
#		resp += "<tr> <td>datestr</td> <td>{}</td> </tr>".format(datestr)
#		resp += "<tr> <td>dtStart</td> <td>{}</td> </tr>".format(dtStart)
#		resp += "<tr> <td>dtEnd</td> <td>{}</td> </tr>".format(dtEnd)
#		resp += "</table>"
#	except Exception as ex:
#		headers = [('Content-type', 'text/plain')]
#		start_response('500 Oops', headers, sys.exc_info())
#		resp = ""
#		resp += str(ex) + '\r'
#		resp += "\r"
#		(exType, exInst, tb) = sys.exc_info()
#		lines = utils.tracebackAsLines(tb)
#		for line in lines:
#			resp += line + "\r"

