# import urllib.parse

import imp
import inspect
import os.path
import sys
import traceback
import jinja2
from splunge import GeneralClientEx
from splunge import InvalidMethodEx
from splunge import ModuleNotFoundEx 
from splunge import MagicLoader
from splunge import PathString
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
#
######################################################################################


def createAndEnhanceModule (moduleName, path):
	module = imp.load_source(moduleName, path)
	module.validateMethod = validateMethod
	return module


def enrichModule (module, env, self):
	reqMethod = env['REQUEST_METHOD']
	module.http = lambda: None 
	module.http.env = env
	module.http.method = env['REQUEST_METHOD']
	module.http.path = PathString(env['PATH_INFO'])
	# module.http.pathParts = env['PATH_INFO'][1:].split('/')
	module.addHeader = lambda x, y: self.response.headers.append((x, y))
	module.validateMethod = lambda x: validateMethod(reqMethod, x) 
	module.setContentType = lambda x: self.response.headers.append(('Content-type', x))
	# import exceptions


def execModule (module):
	attrs1 = set(dir(module))
	module.exec()
	attrs2 = set(dir(module))
	newAttrs = [el for el in attrs2 if el not in attrs1 and el != '__builtins__']
	args = {'http': module.http}
	for attr in newAttrs:
		val = getattr(module, attr)
		if not inspect.isfunction(val) and not inspect.isclass(val):
			args[attr] = getattr(module, attr)
	return args


def execTemplate (templatePath, args):
	jloader = jinja2.FileSystemLoader(os.getcwd())
	jenv = jinja2.Environment()
	templateName = os.path.basename(templatePath)
	jtemplate = jloader.load(jenv, templateName)
	s = jtemplate.render(args)
	return s 


def getModulePath (env):
	path = env['PATH_INFO']
	moduleFilename = path[1:].partition('/')[0] + '.py'
	modulePath = os.path.join(os.getcwd(), moduleFilename)
	return modulePath


def getTemplatePath (env):
	path = env['PATH_INFO']
	templateFilename = path[1:].partition('/')[0] + '.pyp'
	templatePath = os.path.join(os.getcwd(), templateFilename)
	return templatePath


def renderString (s, args):
	jenv = jinja2.Environment()
	jtemplate = jenv.from_string(s)
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
#        (This is all to allow a quick method for a user to write a single python file, which
#         does some processing and then returns a value)
#
#        After name.py is processed (if it existed), splunge looks for name.pyp
#        If name.pyp is found, splunge treats it as a jinja template and renders it.
#
#       Other than some error handling, that's splunge.
#
class Application ():
	def __init__ (self, env, start_response):
		self.env = env
		self.startResponse = start_response
		self.response = Response()
		try:
			modulePath = getModulePath(env)
			print("modulePath={}".format(modulePath))

			try:
				module = MagicLoader.loadModule(modulePath)
				print("module={}".format(module))
				enrichModule(module, env, self)
				args = execModule(module)
			except ModuleNotFoundEx as ex:
				print('Module {} not found - skipping pre-processing'.format(ex.moduleName))
				args = {}
			if '_' in args:
				if isinstance(args['_'], bytes):
					self.response.text = args['_']
				else:
					self.response.text = renderString(str(args['_']), args)
			else:
				templatePath = getTemplatePath(env)
				print("templatePath={}".format(templatePath))
				if not os.path.isfile(templatePath):
					print("template path was not found")
					self.response.headers.append(('Content-Type', 'text/plain'))
					for name in sorted(args):
						value = args[name]
						print("type({})={}".format(value, type(value)))
						self.response.text += "{} = {}\n".format(name, value)
				else:
					print("templatePath=" + templatePath)
					print("About to execute template ...")
					self.response.text = execTemplate(templatePath, args)
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
			for (key, val) in self.response.headers:
				if key.lower() == 'content-type':
					break
			else:
				self.response.headers.append(('Content-Type', 'text/html'))
			self.startResponse('200 OK', self.response.headers)
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
	def __iter__ (self):
		print("__iter__ being called")
		if isinstance(self.response.text, bytes):
			content = self.response.text
		else:
			content = self.response.text.encode('utf-8')
		yield content


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

