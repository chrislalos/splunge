import contextlib
from dataclasses import dataclass
import io
from . import util
from . import Response

@dataclass
class ModuleExecutionResponse:
	response: Response
	stdout: io.StringIO
	context: dict

	def has_stdout(self):
		return not util.is_io_empty(self.stdout)
	
	
	@staticmethod
	def exec_module(module):
		""" Execute an enriched module & return a ModuleExecutionResponse.

		"""
		# Redirect stdout to a new StringIO and execute module
		moduleStdout = io.StringIO()
		with contextlib.redirect_stdout(moduleStdout):
			module.__spec__.loader.exec_module(module)
		# Create the module state
		moduleContext = util.get_module_context(module)
		moduleResponse = module.http.resp
		moduleState = ModuleExecutionResponse(context=moduleContext, stdout=moduleStdout, response=moduleResponse)
		return moduleState


