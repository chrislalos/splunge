import io
import os
from .. import util
from ..Response import Response
from ..Xgi import Xgi
from .HtmlGenHandler import HtmlGenHandler


class PythonTemplateHandler(HtmlGenHandler):
	def get_content_as_filelike(self, context: dict=None):
		return self.xgi.open_template()

	def gen_html(self, f, context: dict=None):
		# Get local path, append .pyp to the path, & confirm the file exists
		templatePath = self.xgi.get_template_path()
		# Load the template & render it w xgi context
		xgi_args = self.xgi.create_args()
		xgi_args.update(context)
		html = util.render_template(templatePath, context)
		return html
