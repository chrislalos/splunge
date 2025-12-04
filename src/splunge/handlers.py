import os.path
import sys
import traceback
from markdown_it import MarkdownIt
from .Response import Response
# from .HttpEnricher import enrich_module
from .EnrichedModule import EnrichedModule
from .Headers import Headers
from . import loggin
from . import ModuleExecutionResponse
from .mimetypes import mimemap
from . import util

handler_map = {'application/x-python-code': "PythonSourceHandler",
               'application/x-splunge-template': "PythonTemplateHandler",
			   'text/markdown': "MarkdownHandler"
              }


def create_mime_handler(wsgi):
	""" Return the appropriate MIME handler for the wsgi. """
	# Get MIME type from path extension
	ext = util.get_path_extension(wsgi)
	mimeType = mimemap.get(ext, None)
	if mimeType is None:
		loggin.warning("No MIME type found for extension: {ext}", ext)
		return None
	# Get handler class name from MIMEType + get the class from current module
	handlerName = handler_map.get(mimeType, "FileHandler")
	module = sys.modules[__name__]
	handlerClassName = getattr(module, handlerName, None)
	if handlerClassName is None:
		loggin.warning("Unable to find handler class: {handlerClassName}", handlerClassName)
	# instantiate handler class + return instance as handler
	handler = handlerClassName()
	loggin.debug(f"create_mime_handler(): type(handler)={type(handler)}")
	if type(handler).__name__ == "FileHandler":
		setattr(handler, "mimeType", mimeType)
	return handler


class FileHandler:
	def __init__(self):
		self.mimeType = None

	def handle_request (self, wsgi):
		loggin.debug(f"FileHandler.handler_request: self.mimeType={self.mimeType}")
		try:
			f = util.open_by_path(wsgi)
			fileWrapper = getattr(wsgi, 'wsgi.file_wrapper', None)		
			resp = respond_with_file(f, self.mimeType, fileWrapper)
			return (resp, True)
		except FileNotFoundError as ex:
			loggin.error(ex, exc_info=True)
			# We want this to be handled at a higher level
			raise ex


class IndexPageHandler:
	''' Handle index page requests by redirection to /index.html. '''
	def handle_request(self, wsgi):
		try:
			location = '/index.html'
			iter = []
			headers = Headers()
			headers.location = location
			statusCode = 303
			statusMessage = f'Redirecting to {location}'
			resp = Response(
				statusCode=statusCode,
				statusMessage=statusMessage,
				headers=headers,
				exc_info=None,
				iter=iter)
			return (resp, True)
		except FileNotFoundError:
			# We want this to be handled at a higher level
			return (None, False)


class MarkdownHandler:
	def handle_request (self, wsgi):
		title = util.get_file_name(wsgi)
		with util.open_by_path(wsgi) as f:
			# @note utf-8 is harcoded here
			content = f.read().decode('utf-8')
		md = MarkdownIt()
		frag = md.render(content).rstrip()
		content = util.html_fragment_to_doc(frag, title=title).encode('utf-8')
		iter = [content]
		contentLength = len(content)
		contentType = "text/markdown"
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = contentType
		resp = Response(
			statusCode=200,
			statusMessage="OK",
			headers=headers,
			exc_info=None,
			iter=iter
		)
		return (resp, True)


class PythonModuleHandler:
	def handle_request (self, wsgi):
		# Load module & create enriched module
		module = util.load_module(wsgi)
		enrichedModule = EnrichedModule(module, wsgi)
		if not module:
			raise Exception(f'module not found: {util.get_module_path(wsgi)}')

		# Execute the module. Let any exceptions propagate.
		result = enrichedModule.exec()
		
		# Is it a redirection? If so, clear the output, and return without checking for a template
		if result.is_redirect():
			resp = Response.create_redirect(result)
			return (resp, True)
		# Does stdout exist? If so, use it for output
		if result.has_stdout():
			loggin.info("about to use stdout as input")
			buf = result.get_stdout_value()
			loggin.debug(f"stdout bytes\n{buf}")
			iter = [buf]
			resp = Response.create_from_result(result, iter)
			return (resp, True)
		# Does _ exist? If so use it as a template
		if result.templateString:
			s = util.render_string(result.templateString, result.context)
			buf = s.encode('utf-8')
			iter = [buf]
			resp = Response.create_from_result(result, iter)
			return (resp, True)
		# If pyp exists, delegate to template handler, else write context directly to response
		templatePath = util.get_template_path(wsgi)
		if os.path.exists(templatePath):
			loggin.debug(f"handing off to PythonTemplateHandler to handle {templatePath}")
			handler = PythonTemplateHandler()
			return handler.handle_request(wsgi, result.context)
		else:
			# Render the content as a nice table
			buf = util.context_to_bytes(result.context)
			iter = [buf]
			resp = Response.create_from_result(result, iter)
			return (resp, True)

		# Load & enrich the module, and add its folder to sys.path
		# module = util.load_module(wsgi)
		# enrichedModule = EnrichedModule(module, wsgi)
		# if not module:
		# 	raise Exception(f'module not found: {util.get_module_path(wsgi)}')
		# enrich_module(module, wsgi)
		# moduleFolder = util.get_module_folder(wsgi)
		# sys.path.append(moduleFolder)

		# # Execute the module
		# try:
		# 	moduleState = ModuleExecutionResponse.exec_module(module)
		# except Exception as ex:
		# 	traceback.print_tb(ex.__traceback__)
		# 	raise ex

		# # Does stdout exist? If so, use it for output
		# if moduleState.has_stdout():
		# 	loggin.info("about to use stdout as input")
		# 	s = moduleState.stdout.getvalue()
		# 	b = s.encode('utf-8')
		# 	moduleState.response.iter = [b]
		# 	loggin.info("returning a			 real tuple")
		# 	return (moduleState.response, True)

		# else:
		# 	# Get output context + template (if any)
		# 	(context, sTemplate) = util.get_module_context(module)
		# 	# Does _ exist? If so use it as a template
		# 	if sTemplate:
		# 		s = util.render_string(sTemplate, context)
		# 		moduleState.response.add_line(s)
		# 	else:
		# 		# If pyp exists, delegate to template handler, else write context directly to response
		# 		templatePath = util.get_template_path(wsgi)
		# 		if os.path.exists(templatePath):
		# 			handler = PythonTemplateHandler()
		# 			return handler.handle_request(wsgi, context)
		# 		else:
		# 			moduleState.response.write_context(context)
		# 			# Render the content as a nice table
		# 	return (moduleState.response, True)
	

class PythonTemplateHandler:
	def __init__ (self, *, encoding='latin-1'):
		self.encoding = encoding

	def handle_request (self, wsgi, context={}):
		# Get local path, append .pyp to the path, & confirm the file exists
		localPath = util.get_local_path(wsgi)
		templatePath = f'{localPath}.pyp'
		# Load the template & render it w wsgi context
		if not os.path.exists(templatePath):
			raise Exception(f'template path not found: {templatePath}')
		wsgi_args = util.create_wsgi_args(wsgi)
		context.update(wsgi_args)
		content = util.render_template(templatePath, context).encode('utf-8')
		iter = [content]
		# encodedContent = content.encode(self.encoding)
		# Initialize the response + return
		contentLength = len(content)
		contentType = 'text/html'
		headers = Headers()
		headers.contentLength = contentLength
		headers.contentType = contentType
		resp = Response(
			statusCode=200,
			statusMessage="OK",
			headers=headers,
			exc_info=None,
			iter=iter
		)
		return (resp, True)
	

def respond_with_file(f, mimeType, fileWrapper) -> Response:
	headers = Headers()	
	headers.contentType = mimeType
	if fileWrapper:
		_32K = 32768
		iter = fileWrapper(f, _32K)
	else:
		with f:
			iter = [f.read()]
			headers.contentLength = len(iter[0])
	resp = Response(
		statusCode=200,
		statusMessage="OK",
		headers=headers,
		exc_info=None,
		iter=iter
	)
	return resp
