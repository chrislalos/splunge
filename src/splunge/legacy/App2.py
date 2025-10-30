from io import StringIO
import os
import os.path
import sys
import traceback
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
	def handleRequest (self, req, resp, templatePath=None):
		# Get module spec
		modulePath = '{}.py'.format(req.localPath)
		# Load and enrich the module
		moduleSpec = util.load_module_spec(modulePath)
		print("moduleSpec={}".format(moduleSpec))
		moduleExtras = util.createModuleExtras(req, resp)
		# Now, execute the enriched module
		moduleState = util.execModuleSpec(moduleSpec, moduleExtras)
		req.args = moduleState.args
		# If the module wrote to stdout, use the stdout concent as the response
		if moduleState.hasStdout:
			s = moduleState.stdout.getvalue()
			resp.iter = [s.encode('latin-1')]
			done = True
		# If the module assigned a value to underscore ('_'), treat the _ value as the response
		elif moduleState.hasShortcut:
			s = util.renderString(req.args['_'], moduleState.args)
			resp.iter = [s.encode('latin-1')]
			done = True
                # If there's no template, print out all module variables as the response
                # ? Is the content type here going to be a problem? Doesn't this need to be text/plain?
		elif not templatePath:
			for key, val in req.args.items():
				line = '{}={}'.format(key, val)
				resp.addLine(line)
			done = True
		# Use PythonTemplateHandler to render the template
		else:
			req.args = moduleState.args
			handler = PythonTemplateHandler(req.args)
			done = handler.handleRequest(req, resp)
		return done


class PythonHandler:
	def handleRequest (self, req, resp):
		def sendResponse (req, resp, moduleState):
			if moduleState.stdout:
				print('*** moduleState.stdout found')
				s = moduleState.stdout.getvalue()
				resp.iter = [s.encode('latin-1')]
				done = True
			elif moduleState.shortcut:
				print('*** moduleState.shortcut found')
				s = util.renderString(moduleState.args['_'], moduleState.args)
				resp.iter = [s.encode('latin-1')]
				done = True
			else:
				templatePath = '{}.pyp'.format(req.localPath)
				if not os.path.isfile(templatePath):
					print('*** templatePath not found: dumping moduleState.args')
					for key, val in moduleState.args.items():
						line = '{}={}'.format(key, val)
						resp.addLine(line)
					done = True
				else:
					print('*** templatePath found: forwarding to template handler')
					req.args = moduleState.args
					handler = PythonTemplateHandler(req.args)
					done = handler.handleRequest(req, resp)
			return done

		# Do module
		module = util.createModule(req, resp)
		moduleState = util.execModule(module)
		done = sendResponse(req, resp, moduleState)
		return done


#  		handler = PythonCodeHandler()
# 		templatePath = '{}.pyp'.format(req.localPath)
# 		if not os.path.isfile(templatePath):
# 			templatePath = None	
# 		if handler.handleRequest(req, resp, templatePath=templatePath):
# 			done = True
# 		else:
# 			templatePath = '{}.pyp'.format(req.localPath)
# 			if not os.path.isfile(templatePath):
# 				done = True
# 			else:
# 				print("*** path before: {}".format(req.path))
# 				req.env['PATH_INFO'] = req.path + '.pyp'
# 				print("*** path after: {}".format(req.path))
# 				handler = PythonTemplateHandler(req.args)
# 				done = handler.handleRequest(req, resp)


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
		if os.path.isfile(req.localPath):
			templatePath = req.localPath
		else:
			templatePath = '{}.pyp'.format(req.localPath)
		print('templatePath={}'.format(templatePath))
		content = util.renderTemplate(templatePath, self.args)
		encodedContent = content.encode(self.encoding)
		resp.iter = [encodedContent]
		return True



HandlerMap = {'application/x-python-code': PythonSourceHandler,
              'application/x-splunge-template': PythonTemplateHandler
             }


# Determine the appropriate handler for the path entered by the user
# 
def getHandler (req):
	print("req.localPath={}".format(req.localPath))
	ext = req.getPathExtension()
	# Is the path a non-existent FILE and does it lack an extension? (e.g. http://foo.com/app/user)  
	if not ext and not os.path.isfile(req.localPath):
		# If it exists (as a file) when we append .py, use PythonHandler
		modulePath = '{}.py'.format(req.localPath)
		if os.path.isfile(modulePath):
			handlerClass = PythonHandler
		# If it exists (as a file) when we append .pyp, use PythonTemplateHandler
		else:		
			templatePath = '{}.pyp'.format(req.localPath)
			if os.path.isfile(templatePath):
				handlerClass = PythonTemplateHandler
			else:
				handlerClass = None
	# It it has an extension, get the mime type appropriate to its extension
	else:
		# If the mimeType doesn't exist, use None.
		# If the mimeType exists, and it does not have a handler in HandlerMap, use FileHandler 
		mimetype = mimetypes.map.get(ext, None)
		handlerClass = HandlerMap.get(mimetype, FileHandler)
	# If there is a handlerClass, instantiate it and return it. Otherwise return None.
	print("handlerClass={}".format(handlerClass))
	if not handlerClass:
		handler = None
	else:
		handler = handlerClass()
	return handler


# Write the stacktrace to the response, so that it appears in the browser (useful for debugging)
def captureTraceback (resp, exc_info=None):
	if not exc_info:
		exc_info = sys.exc_info()
	resp.exc_info = exc_info
	(exType, exMessage, tb) = exc_info
	tbTuples = traceback.extract_tb(tb)
	tbLines = [formatTracebackLine(tbTuple) for tbTuple in tbTuples]
	resp.addLines(tbLines)
	exLine = '{}: {}'.format(exType.__name__, exMessage)
	print('*** exLine: {}'.format(exLine))
	resp.addLine(exLine)


# Extract the relevant bits from a traceback line and format said relevant bits
def formatTracebackLine (tbTuple):
	(filename, lineNumber, functionName, text) = tbTuple
	tbLine = '{}:{} {}(): {}'.format(filename, lineNumber, functionName, text)
	return tbLine

# Handle 404s
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

def getPathExtension (path):
	(_, ext) = os.path.splitext(path)
	return ext

# Define the functions required by WSGI (in PEP 444)
class Application:
    def __init__ (self):
        self.sessionMap = {}

    def __call__ (self, env, start_response):
        print("I'm in call()!")
        try:
            resp = Response()
            print("self.headers={}".format(resp.headers))
            req = Request(env)
            handler = getHandler(req)
            # @note Do I really want to treat handler.handleRequest() => None/False, as a 404, in all circumstances?
            if not handler or not handler.handleRequest(req, resp):
                handleFileNotFound(req, resp)	
        except:
            handleInternalError(resp)
        for key, value in sorted(resp.headers()):
            print("{}: {}".format(key, value))
        start_response(resp.status, resp.headers(), resp.exc_info)
        return resp.iter

application = Application()
