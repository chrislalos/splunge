import contextlib
from dataclasses import dataclass
import io
import sys
import types
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from _typeshed.wsgi import WSGIEnvironment
from .Headers import Headers
from .HttpEnricher import HttpEnricher
from .Xgi import Xgi
from . import util

class EnrichedModule:
	module: types.ModuleType
	xgi: Xgi

	# http
	@property
	def http(self) -> HttpEnricher: return getattr(self.module, "http", None)
	@http.setter
	def	http(self, val): setattr(self.module, 'http', val)

	@classmethod
	def create(cls, xgi: Xgi)-> "EnrichedModule":
		module = xgi.load_module()
		obj = EnrichedModule(module, xgi)
		return obj

	def __init__(self, module: types.ModuleType, xgi: Xgi) -> None:
		self.module = module
		self.xgi = xgi
		self.http = HttpEnricher(xgi)	# will set module.http as a side effect


	def exec(self) -> "EnrichedModuleResult":
		moduleFolder = self.xgi.get_module_folder()
		sys.path.append(moduleFolder)

		# use the module's spec's loader to execute the module in a stdout-capturing context
		stdout = io.StringIO()
		with contextlib.redirect_stdout(stdout):
			self.module.__spec__.loader.exec_module(self.module)

		# get the context + templateString from the module
		context = self.get_context()
		templateString = self.get_template_string()

		# create + return the result object
		result = EnrichedModuleResult(
			headers=self.http.headers,
			statusCode=self.http.statusCode,
			statusMessage=self.http.statusMessage,
			stdout=stdout,
			context=context,
			templateString=templateString
		)
		return result
	

	def get_context(self):
		attrs = util.get_module_attrs(self.module)
		attrs.pop('http', None)
		attrs.pop('_', None)
		return attrs

	
	def get_template_string(self):
		attrs = util.get_module_attrs(self.module)
		templateString = attrs.pop('_', None)
		return templateString


@dataclass(kw_only=True)
class EnrichedModuleResult:
	headers: Headers
	statusCode: int
	statusMessage: str
	stdout: io.TextIOBase
	context: dict
	templateString: str

	@classmethod
	def createEmpty(cls) -> "EnrichedModuleResult":
		return EnrichedModuleResult(
			headers=None,
			statusCode=0,
			statusMessage="",
			stdout=io.StringIO(),
			context={},
			templateString=""
		)

	@property
	def status(self): return f"{self.statusCode} {self.statusMessage}"
	@status.setter
	def status(self, val: str):
		sStatusCode, _, self.statusMessage = val.partition(' ')
		self.statusCode = int(sStatusCode)

	def get_stdout_value(self) -> bytes:
		if not self.has_stdout():
			return bytes()
		self.stdout.seek(0, io.SEEK_SET)
		s = self.stdout.read()
		buf = s.encode('utf-8')
		return buf
	
	def has_stdout(self):
		if not self.stdout:
			return False
		return not util.is_io_empty(self.stdout)

	def is_redirect(self):
		status_codes = [301, 303, 307, 308]
		return self.statusCode in status_codes



