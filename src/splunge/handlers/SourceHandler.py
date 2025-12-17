import io
import pygments
import pygments.formatters
import pygments.lexers
from ..Response import Response
from ..Xgi import Xgi
from .HtmlGenHandler import HtmlGenHandler

source_handler_map = {
	'application/x-python-code': pygments.lexers.PythonLexer,
	'application/x-splunge-template': pygments.lexers.DjangoLexer,
}


class SourceHandler(HtmlGenHandler):
	def gen_html(self, f, context:dict=None):
		from . import lookup_mime_type
		with f:
			code = f.read()
		formatter =  pygments.formatters.HtmlFormatter(full=True, linenos=True)
		mimeType = lookup_mime_type(self.xgi)
		lexerClass = source_handler_map[mimeType]
		lexer = lexerClass()
		html  = pygments.highlight(code, lexer, formatter)
		return html
