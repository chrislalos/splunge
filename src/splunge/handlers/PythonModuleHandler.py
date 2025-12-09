import os
from .. import loggin, util
from ..EnrichedModule import EnrichedModule
from ..Response import Response
from ..Xgi import Xgi
from .BaseHandler import BaseHandler
from .PythonTemplateHandler import PythonTemplateHandler


class PythonModuleHandler(BaseHandler):
	def handle_request(self) -> Response:
		# Load module, create & exec enriched module
		module = self.xgi.load_module()
		enrichedModule = EnrichedModule(module, self.xgi)
		if not module:
			raise Exception(f'module not found: {util.get_module_path(self.xgi)}')
		result = enrichedModule.exec()
		
		# If redirection, clear the output, and return without checking for a template
		if result.is_redirect():
			resp = Response.create_redirect(result.statusCode, result.statusMessage, result.headers.location)
		# If stdout exists, use it for output
		elif result.has_stdout():
			loggin.info("about to use stdout as input")
			buf = result.get_stdout_value()
			loggin.debug(f"stdout bytes\n{buf}")
			iter = [buf]
			resp = Response.create_from_result(result, iter)
		# If _ exists, use it as a template
		elif result.templateString:
			s = util.render_string(result.templateString, result.context)
			buf = s.encode('utf-8')
			iter = [buf]
			resp = Response.create_from_result(result, iter)
		# If pyp exists, delegate to template handler, else write context directly to response
		elif self.xgi.has_template_path():
			handler = PythonTemplateHandler(self.xgi)
			resp =  handler.handle_request(result.context)
		else:
			# Render the content as a nice table
			buf = util.context_to_bytes(result.context)
			iter = [buf]
			resp = Response.create_from_result(result, iter)
		return resp
