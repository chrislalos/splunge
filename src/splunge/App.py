from io import StringIO
import os
import os.path
import sys
import traceback
import urllib.parse
import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from splunge import mimetypes, PathString, util
from splunge.Request import Request
from splunge.Response import Response

_32K = 32768


def openByPath (req):
	print("localPath={}".format(req.localPath))
	f = open(req.localPath, 'rb')
	return f
	

def respondWithFile (req, resp, f):
	if 'wsgi.file_wrapper' in req.env:
		file_wrapper = req.env['wsgi.file_wrapper']
		resp.iter = file_wrapper(f, _32K)
	else:
		resp.iter = f


class FileHandler:
	def handleRequest (self, req, resp):
		done = False
		try:
			f = openByPath(req)
			respondWithFile(req, resp, f)
			done = True
		except FileNotFoundError:
			# We want this to be handled at a higher level
			pass
		return done


class PythonCodeHandler:
	def handleRequest (self, req, resp):
		# Get module spec
		modulePath = '{}.py'.format(req.localPath)
		# Load and enrich the module
		moduleSpec = util.load_module_spec(modulePath)
		print("moduleSpec={}".format(moduleSpec))
		moduleExtras = util.createModuleExtras(req, resp)
		util.execModuleSpec(moduleSpec, moduleExtras)
		req.args = moduleSpec.args
		done = not moduleSpec.gotoTemplate
		return done


class PythonModuleHandler:
	def handleRequest (self, req, resp):
		handler = PythonCodeHandler()
		if handler.handleRequest(req, resp):
			done = True
		else:
			templatePath = '{}.pyp'.format(req.localPath)
			if not os.path.isfile(templatePath):
				done = True
			else:
				print("*** path before: {}".format(req.path))
				req.env['PATH_INFO'] = req.path + '.pyp'
				print("*** path after: {}".format(req.path))
				handler = PythonTemplateHandler(req.args)
				done = handler.handleRequest(req, resp)
		return done


class PythonSourceHandler:
	_lexer = PythonLexer()
	_formatter = HtmlFormatter(full=True, linenos=True)

	def handleRequest (self, req, resp):
		done = False
		try:
			f = openByPath(req)
			code = f.read()
			resp.iter = [self.highlightCode(code)]
			done = True
		except FileNotFoundError:
			# We want this to be handled at a higher level
			pass	
		return done

	def highlightCode (self, code, *, encoding='latin-1'):
		highlightedCode = pygments.highlight(code, self.__class__._lexer, self.__class__._formatter)
		highlightedCodeBytes = highlightedCode.encode(encoding)
		return highlightedCodeBytes


class PythonTemplateHandler:
	def __init__ (self, args=None, *, encoding='latin-1'):
		self.args = args
		self.encoding = encoding

	def handleRequest (self, req, resp):
		content = util.renderTemplate(req.localPath, self.args)
		encodedContent = content.encode(self.encoding)
		resp.iter = [encodedContent]
		return True



HandlerMap = {'application/x-python-code': PythonSourceHandler,
              'application/x-splunge-template': PythonTemplateHandler
             }



def getHandler (req):
	(_, ext) = os.path.splitext(req.localPath)
	print("ext={}".format(ext))
	# If there is no extension and the file does not exist, treat it as a Python module
	if not ext and not os.path.isfile(req.localPath):
		handlerClass = PythonModuleHandler
	else:
		# Defaults: mimetype=None, handlerClass=FileHandler
		mimetype = mimetypes.map.get(ext, None)
		handlerClass = HandlerMap.get(mimetype, FileHandler)
	print("handlerClass={}".format(handlerClass))
	handler = handlerClass()
	return handler


def captureTraceback (resp, exc_info=None):
	if not exc_info:
		exc_info = sys.exc_info()
	resp.exc_info = exc_info
	(exType, exMessage, tb) = exc_info
	exLine = '{}: {}'.format(exType, exMessage)
	resp.addLine(exLine)
	tbTuples = traceback.extract_tb(tb)
	tbLines = [formatTracebackLine(tbTuple) for tbTuple in tbTuples]
	resp.addLines(tbLines)


def formatTracebackLine (tbTuple):
	(filename, lineNumber, functionName, text) = tbTuple
	tbLine = '{}:{} {}(): {}'.format(filename, lineNumber, functionName, text)
	return tbLine


def handleFileNotFound (req, resp):
	resp.status = (404, 'File Not Found')
	resp.clearHeaders()
	resp.setHeader('Content-type', 'text/plain')
	line = 'No resource found for {}'.format(req.path)
	resp.addLine(line)


def handleInternalError (resp):
	traceback.print_exc()
	resp.status = (500, 'Server Error')
	resp.clearHeaders()
	resp.setHeader('Content-type', 'text/plain')
	captureTraceback(resp)


class Application:
	def __call__ (self, env, start_response):
		try:
			req = Request(env)
			resp = Response()
			handler = getHandler(req)
			if not handler.handleRequest(req, resp):
				handleFileNotFound(req, resp)	
		except:
			handleInternalError(resp)
		start_response(resp.status, resp.headers, resp.exc_info)
		return resp.iter

application = Application()
