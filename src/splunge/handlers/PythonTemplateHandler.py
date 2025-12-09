import io
import os
from .. import loggin, util
from ..Response import Response
from ..Xgi import Xgi
from .HtmlGenHandler import HtmlGenHandler


class PythonTemplateHandler(HtmlGenHandler):
	def open_content(self):
		loggin.debug(f'{self.__class__.__name__}.open_content()')
		return self.xgi.open_template()

	def gen_html(self, f, context: dict=None):
		loggin.debug(f'{self.__class__.__name__}.get_html()')
		# Get local path, append .pyp to the path, & confirm the file exists
		templatePath = self.xgi.get_template_path()
		loggin.debug(f'templatePath={templatePath}')
		# Load the template & render it w xgi context
		xgi_args = self.xgi.create_args()
		xgi_args.update(context)
		html = util.render_template(templatePath, context)
		return html
