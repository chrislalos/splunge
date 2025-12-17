from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
# from .HttpEnricher import enrich_module
from .EnrichedModule import EnrichedModule
from . import loggin
from .mimetypes import mimemap
from .handlers.SourceHandler import SourceHandler

handler_map = {'application/x-python-code': "SourceHandler",
               'application/x-splunge-template': "SourceHandler",
			   'text/markdown': "MarkdownHandler"
              }

@dataclass

def create_mime_handler(xgi):
	""" Return the appropriate MIME handler for the xgi. """
	# Get MIME type from path extension
	ext = xgi.get_path_extension()
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
	if handlerName == "SourceHandler":
		handler = SourceHandler.create(mimeType)
	else:
		handler = handlerClassName()
	loggin.debug(f"create_mime_handler(): type(handler)={type(handler)}")
	if type(handler).__name__ == "FileHandler":
		setattr(handler, "mimeType", mimeType)
	return handler


### legacy - PythonSourceHandler.handler_rquest()
#
# Load & enrich the module, and add its folder to sys.path
# module = util.load_module(xgi)
# enrichedModule = EnrichedModule(module, xgi)
# if not module:
# 	raise Exception(f'module not found: {util.get_module_path(xgi)}')
# enrich_module(module, xgi)
# moduleFolder = util.get_module_folder(xgi)
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
# 		templatePath = util.get_template_path(xgi)
# 		if os.path.exists(templatePath):
# 			handler = PythonTemplateHandler()
# 			return handler.handle_request(xgi, context)
# 		else:
# 			moduleState.response.write_context(context)
# 			# Render the content as a nice table
# 	return (moduleState.response, True)

