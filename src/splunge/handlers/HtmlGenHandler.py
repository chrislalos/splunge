from abc import abstractmethod
import io
import pygments
import pygments.formatters
import pygments.lexers
from .. import loggin
from ..Response import Response
from ..Xgi import Xgi
from .FileHandler import FileHandler

'''
HtmlGenHandler

A common base class for handlers that generate HTML, though typically are based
on resources that are not themselves HTML. Some examples

- Source code that is syntax highlighted and rendered as HTML
- Jinja templates for the output of an executed Python module
- Documentation formats like Markdown (.md)

HtmlGenHandler refines FileHandler's handle_request(). FileHandler
creates its content as a filelike and then it creates a Response
object based on the value of the xgi's file_wrapper. HtmlGenHandler
refines get_content_as_filelike() to call a method that generates
Html, and then wraps the Html in a io.BytesIO to create a filelike.

This abstract method is called gen_html(). Subclasses of HtmlGetHandler
will define get_html(). HtmlGenHandler provides the rest.

HtmlGenHandler also defines the handler MIME type as
text/html; charset=utf-8
'''

source_handler_map = {
	'application/x-python-code': pygments.lexers.PythonLexer,
	'application/x-splunge-template': pygments.lexers.DjangoLexer,
}


class HtmlGenHandler(FileHandler):
	@abstractmethod
	def gen_html(self, f, context:dict=None):
		loggin.debug(f'{self.__class__.__name__}.get_html')
		pass

	def get_output_as_filelike(self, context: dict=None):
		loggin.debug(f'{self.__class__.__name__}.get_output_as_filelike')
		f = self.open_content()
		html = self.gen_html(f, context)
		fContent = io.BytesIO(html.encode('utf-8'))
		return fContent

	def open_content(self):
		return self.xgi.open_by_path()

	def get_mime_type(self) -> str:
		return "text/html; charset=utf-8"
